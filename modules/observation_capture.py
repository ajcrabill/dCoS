"""Auto-Capture Hooks: Automatic observation logging.

Installs hooks into key dCoS workflows to auto-capture observations without
requiring user action.
"""

from datetime import datetime
from typing import Dict, Any, Callable, List
import sqlite3
import json
from uuid import uuid4


class ObservationCapture:
    """Central capture system for all observations."""

    def __init__(self, db_connection: sqlite3.Connection):
        self.db = db_connection
        self._ensure_tables_exist()
        self.hooks: Dict[str, List[Callable]] = {}

    def _ensure_tables_exist(self):
        """Create observation tables if needed."""
        cursor = self.db.cursor()

        # Raw observations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY,
                observation_type TEXT,
                source TEXT,
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                importance_score REAL DEFAULT 1.0
            )
        """)

        self.db.commit()

    def capture(self, observation_type: str, source: str, data: Dict[str, Any]) -> str:
        """Capture an observation.

        Args:
            observation_type: Type of observation (email, calendar, etc.)
            source: System that generated the observation
            data: Raw observation data

        Returns:
            Observation ID
        """
        obs_id = str(uuid4())

        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO observations (id, observation_type, source, raw_data)
            VALUES (?, ?, ?, ?)
        """, (obs_id, observation_type, source, json.dumps(data)))

        self.db.commit()
        return obs_id

    def capture_email(self, from_addr: str, subject: str, received_at: datetime, thread_id: str):
        """Auto-capture email received."""
        self.capture("email_received", "gmail", {
            "from": from_addr,
            "subject": subject,
            "received_at": received_at.isoformat(),
            "thread_id": thread_id
        })

    def capture_calendar_event(self, event_title: str, starts_at: datetime, ends_at: datetime, attendees: List[str]):
        """Auto-capture calendar event."""
        self.capture("calendar_event", "gcal", {
            "title": event_title,
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
            "attendees": attendees
        })

    def capture_obligation(self, task: str, deadline: datetime, priority: str):
        """Auto-capture obligation created."""
        self.capture("obligation_created", "dcos", {
            "task": task,
            "deadline": deadline.isoformat(),
            "priority": priority
        })

    def capture_rule_triggered(self, rule_id: str, condition: str, action: str, triggered_at: datetime):
        """Auto-capture rule triggered."""
        self.capture("rule_triggered", "dcos", {
            "rule_id": rule_id,
            "condition": condition,
            "action": action,
            "triggered_at": triggered_at.isoformat()
        })

    def capture_vault_change(self, file_path: str, change_type: str, content_summary: str = None):
        """Auto-capture vault note change."""
        self.capture("vault_change", "obsidian", {
            "file_path": file_path,
            "change_type": change_type,  # created, modified, deleted
            "content_summary": content_summary
        })

    def register_hook(self, hook_name: str, callback: Callable):
        """Register additional hook callback.

        Args:
            hook_name: Name of hook (e.g., "on_email_received")
            callback: Function to call when hook fires
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)

    def trigger_hook(self, hook_name: str, *args, **kwargs):
        """Trigger all callbacks for a hook.

        Args:
            hook_name: Name of hook
            *args, **kwargs: Arguments to pass to callbacks
        """
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Hook callback error in {hook_name}: {e}")
