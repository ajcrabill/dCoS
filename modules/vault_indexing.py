"""
Vault Indexing - Convert Obsidian vault into queryable database.

Implements vault-db pattern: SQLite-backed full-text search, backlinks,
and relationship tracking for Obsidian vaults.

Supports:
- FTS5 full-text search over note titles and bodies
- Wikilink and markdown link tracking
- Backlink discovery
- Orphan detection (notes with no incoming links)
- Container-based organization
- Tag extraction and querying
- Frontmatter metadata indexing
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import yaml
import re
from datetime import datetime


class VaultIndexer:
    """Index and maintain Obsidian vault searchability."""

    def __init__(self, vault_path: Path, db_path: Path):
        """
        Initialize vault indexer.

        Args:
            vault_path: Path to Obsidian vault root
            db_path: Path to SQLite database for index
        """
        self.vault_path = Path(vault_path)
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema."""
        cursor = self.conn.cursor()

        # Vault index table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_index (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                title TEXT,
                container TEXT,
                mtime REAL NOT NULL,
                size INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # FTS5 full-text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS vault_search USING fts5(
                title, body, path UNINDEXED
            )
        """)

        # Frontmatter metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_frontmatter (
                id INTEGER PRIMARY KEY,
                note_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY(note_id) REFERENCES vault_index(id) ON DELETE CASCADE
            )
        """)

        # Tags
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_tags (
                id INTEGER PRIMARY KEY,
                note_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                UNIQUE(note_id, tag),
                FOREIGN KEY(note_id) REFERENCES vault_index(id) ON DELETE CASCADE
            )
        """)

        # Wikilinks and markdown links
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_links (
                id INTEGER PRIMARY KEY,
                from_note_id INTEGER NOT NULL,
                to_path TEXT NOT NULL,
                link_type TEXT,  -- wikilink, markdown_link
                FOREIGN KEY(from_note_id) REFERENCES vault_index(id) ON DELETE CASCADE
            )
        """)

        # Backlinks (computed)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_backlinks (
                id INTEGER PRIMARY KEY,
                note_id INTEGER NOT NULL,
                from_note_id INTEGER NOT NULL,
                UNIQUE(note_id, from_note_id),
                FOREIGN KEY(note_id) REFERENCES vault_index(id),
                FOREIGN KEY(from_note_id) REFERENCES vault_index(id)
            )
        """)

        self.conn.commit()

    def sync(self, force: bool = False) -> Dict[str, int]:
        """
        Sync vault with index. Only processes changed files unless force=True.

        Returns:
            Dictionary with counts: {indexed, deleted, updated}
        """
        stats = {"indexed": 0, "deleted": 0, "updated": 0}

        # Find all markdown files
        md_files = list(self.vault_path.glob("**/*.md"))

        # Get currently indexed files
        cursor = self.conn.cursor()
        cursor.execute("SELECT path FROM vault_index")
        indexed_paths = {row[0] for row in cursor.fetchall()}

        # Process each file
        for md_file in md_files:
            try:
                rel_path = str(md_file.relative_to(self.vault_path))

                if rel_path not in indexed_paths or force:
                    self._index_file(md_file, rel_path)
                    stats["indexed"] += 1
                elif force:
                    stats["updated"] += 1
            except Exception as e:
                print(f"Error indexing {md_file}: {e}")

        # Clean up deleted files
        for indexed_path in indexed_paths:
            full_path = self.vault_path / indexed_path
            if not full_path.exists():
                cursor.execute("DELETE FROM vault_index WHERE path = ?", (indexed_path,))
                stats["deleted"] += 1

        self.conn.commit()
        return stats

    def _index_file(self, file_path: Path, rel_path: str):
        """Index a single markdown file."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except:
            return

        # Extract frontmatter and body
        frontmatter, body = self._parse_frontmatter(content)
        title = frontmatter.get('title', file_path.stem)

        # Determine container
        parts = rel_path.split('/')
        container = parts[0] if len(parts) > 1 else 'uncategorized'

        # Get file stats
        stat = file_path.stat()
        mtime = stat.st_mtime
        size = stat.st_size

        # Upsert into vault_index
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO vault_index (path, title, container, mtime, size, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (rel_path, title, container, mtime, size))

        note_id = cursor.lastrowid

        # Index for full-text search
        cursor.execute(
            "INSERT OR REPLACE INTO vault_search (title, body, path) VALUES (?, ?, ?)",
            (title, body, rel_path)
        )

        # Extract and index metadata
        for key, value in frontmatter.items():
            cursor.execute("""
                INSERT OR REPLACE INTO vault_frontmatter (note_id, key, value)
                VALUES (?, ?, ?)
            """, (note_id, key, json.dumps(value) if not isinstance(value, str) else value))

        # Extract and index tags
        tags = self._extract_tags(body)
        for tag in tags:
            cursor.execute("""
                INSERT OR IGNORE INTO vault_tags (note_id, tag)
                VALUES (?, ?)
            """, (note_id, tag))

        # Extract and index links
        links = self._extract_links(body)
        for link_path, link_type in links:
            cursor.execute("""
                INSERT INTO vault_links (from_note_id, to_path, link_type)
                VALUES (?, ?, ?)
            """, (note_id, link_path, link_type))

        self.conn.commit()

    def _parse_frontmatter(self, content: str) -> tuple:
        """Extract YAML frontmatter and body."""
        if not content.startswith('---'):
            return {}, content

        try:
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm_text = parts[1].strip()
                body = parts[2].strip()
                frontmatter = yaml.safe_load(fm_text) or {}
                return frontmatter, body
        except:
            pass

        return {}, content

    def _extract_tags(self, text: str) -> set:
        """Extract #tag occurrences."""
        tags = set()
        for match in re.finditer(r'#[\w-]+', text):
            tags.add(match.group(0)[1:])  # Remove #
        return tags

    def _extract_links(self, text: str) -> List[tuple]:
        """Extract wikilinks and markdown links."""
        links = []

        # Wikilinks: [[path]] or [[path|display]]
        for match in re.finditer(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', text):
            links.append((match.group(1), 'wikilink'))

        # Markdown links: [text](path)
        for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', text):
            path = match.group(2)
            if not path.startswith(('http://', 'https://', 'mailto:')):
                links.append((path, 'markdown_link'))

        return links

    def update_backlinks(self):
        """Compute and update backlinks table."""
        cursor = self.conn.cursor()

        # Clear existing backlinks
        cursor.execute("DELETE FROM vault_backlinks")

        # Recompute from links
        cursor.execute("""
            SELECT from_note_id, to_path FROM vault_links
        """)

        for from_note_id, to_path in cursor.fetchall():
            # Find note_id for to_path
            cursor.execute(
                "SELECT id FROM vault_index WHERE path = ?",
                (to_path,)
            )
            result = cursor.fetchone()
            if result:
                to_note_id = result[0]
                cursor.execute("""
                    INSERT OR IGNORE INTO vault_backlinks (note_id, from_note_id)
                    VALUES (?, ?)
                """, (to_note_id, from_note_id))

        self.conn.commit()


class VaultQuery:
    """Query interface for vault index."""

    def __init__(self, indexer: VaultIndexer):
        self.indexer = indexer
        self.conn = indexer.conn

    def search(self, query: str, container: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Full-text search across vault."""
        cursor = self.conn.cursor()

        if container:
            cursor.execute("""
                SELECT vi.path, vi.title, vi.container, COUNT(vb.from_note_id) as backlinks
                FROM vault_search vs
                JOIN vault_index vi ON vs.path = vi.path
                LEFT JOIN vault_backlinks vb ON vi.id = vb.note_id
                WHERE vault_search MATCH ? AND vi.container = ?
                GROUP BY vi.id
                ORDER BY vs.rank
                LIMIT ?
            """, (query, container, limit))
        else:
            cursor.execute("""
                SELECT vi.path, vi.title, vi.container, COUNT(vb.from_note_id) as backlinks
                FROM vault_search vs
                JOIN vault_index vi ON vs.path = vi.path
                LEFT JOIN vault_backlinks vb ON vi.id = vb.note_id
                WHERE vault_search MATCH ?
                GROUP BY vi.id
                ORDER BY vs.rank
                LIMIT ?
            """, (query, limit))

        return [
            {
                "path": row[0],
                "title": row[1],
                "container": row[2],
                "backlinks": row[3]
            }
            for row in cursor.fetchall()
        ]

    def find_backlinks(self, path: str) -> List[Dict]:
        """Find all notes linking to a given note."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT vi.path, vi.title
            FROM vault_backlinks vb
            JOIN vault_index from_vi ON vb.from_note_id = from_vi.id
            JOIN vault_index vi ON vb.note_id = vi.id
            WHERE vi.path = ?
        """, (path,))

        return [
            {"path": row[0], "title": row[1]}
            for row in cursor.fetchall()
        ]

    def find_orphans(self, container: Optional[str] = None) -> List[Dict]:
        """Find notes with no incoming links."""
        cursor = self.conn.cursor()

        if container:
            cursor.execute("""
                SELECT vi.path, vi.title, vi.container
                FROM vault_index vi
                LEFT JOIN vault_backlinks vb ON vi.id = vb.note_id
                WHERE vb.note_id IS NULL AND vi.container = ?
                ORDER BY vi.title
            """, (container,))
        else:
            cursor.execute("""
                SELECT vi.path, vi.title, vi.container
                FROM vault_index vi
                LEFT JOIN vault_backlinks vb ON vi.id = vb.note_id
                WHERE vb.note_id IS NULL
                ORDER BY vi.title
            """)

        return [
            {"path": row[0], "title": row[1], "container": row[2]}
            for row in cursor.fetchall()
        ]

    def query_by_container(self, container: str) -> List[Dict]:
        """Get all notes in a container."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT path, title FROM vault_index
            WHERE container = ?
            ORDER BY title
        """, (container,))

        return [
            {"path": row[0], "title": row[1]}
            for row in cursor.fetchall()
        ]

    def query_by_tag(self, tag: str) -> List[Dict]:
        """Get all notes with a specific tag."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT vi.path, vi.title
            FROM vault_tags vt
            JOIN vault_index vi ON vt.note_id = vi.id
            WHERE vt.tag = ?
            ORDER BY vi.title
        """, (tag,))

        return [
            {"path": row[0], "title": row[1]}
            for row in cursor.fetchall()
        ]

    def query_by_metadata(self, key: str, value: Optional[str] = None) -> List[Dict]:
        """Query by frontmatter metadata."""
        cursor = self.conn.cursor()

        if value:
            cursor.execute("""
                SELECT vi.path, vi.title
                FROM vault_frontmatter vf
                JOIN vault_index vi ON vf.note_id = vi.id
                WHERE vf.key = ? AND vf.value = ?
                ORDER BY vi.title
            """, (key, value))
        else:
            cursor.execute("""
                SELECT vi.path, vi.title
                FROM vault_frontmatter vf
                JOIN vault_index vi ON vf.note_id = vi.id
                WHERE vf.key = ?
                ORDER BY vi.title
            """, (key,))

        return [
            {"path": row[0], "title": row[1]}
            for row in cursor.fetchall()
        ]
