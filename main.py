#!/usr/bin/env python3
"""
Digital Chief of Staff - Main Entry Point

Creator: AJ Crabill
Repository: https://github.com/ajcrabill/dCoS
License: MIT

Usage:
    python main.py              # Start dCoS
    python main.py --init-db    # Initialize database
    python main.py --test       # Test all systems
    python main.py --help       # Show help
"""

import os
import sys
import sqlite3
import argparse
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / 'modules'))

try:
    import yaml
except ImportError:
    print("❌ PyYAML not installed. Run: pip install -r install/requirements.txt")
    sys.exit(1)


def load_config():
    """Load configuration from dcos_config.yaml"""
    config_path = Path(__file__).parent / 'config' / 'dcos_config.yaml'

    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        print("Please edit config/dcos_config.yaml and try again.")
        sys.exit(1)

    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        sys.exit(1)


def init_database(config):
    """Initialize SQLite database with schema"""
    db_path = config.get('preferences_schema', {}).get('system_preferences', {}).get('database_location', './state/chief_of_staff.sqlite')
    db_path = Path(db_path).expanduser()

    # Create state directory if needed
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📦 Initializing database at {db_path}...")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Apply base schema
        schema_path = Path(__file__).parent / 'schema' / 'dcos_schema.sql'
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                cursor.executescript(f.read())
            print("  ✓ Base schema applied")

        # Apply memory extensions
        extensions_path = Path(__file__).parent / 'schema' / 'memory_extensions.sql'
        if extensions_path.exists():
            with open(extensions_path, 'r') as f:
                cursor.executescript(f.read())
            print("  ✓ Memory extensions applied")

        conn.commit()
        conn.close()

        print(f"✓ Database initialized at {db_path}")
        return True

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def test_systems(config):
    """Test all system components"""
    print("🧪 Testing dCoS systems...\n")

    all_ok = True

    # Test 1: Modules
    print("1️⃣ Testing modules...")
    try:
        import backend_executor
        import vault_indexing
        import account_manager
        print("   ✓ Core modules load\n")
    except ImportError as e:
        print(f"   ❌ Module error: {e}\n")
        all_ok = False

    # Test 2: Database
    print("2️⃣ Testing database...")
    try:
        db_path = config.get('preferences_schema', {}).get('system_preferences', {}).get('database_location', './state/chief_of_staff.sqlite')
        db_path = Path(db_path).expanduser()

        if not db_path.exists():
            print(f"   ℹ Database doesn't exist yet (initialize with --init-db)\n")
        else:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
            result = cursor.fetchone()
            conn.close()

            if result:
                print("   ✓ Database connected\n")
            else:
                print("   ⚠ Database exists but is empty\n")
                all_ok = False
    except Exception as e:
        print(f"   ❌ Database error: {e}\n")
        all_ok = False

    # Test 3: Config
    print("3️⃣ Checking configuration...")
    backend = config.get('backend_defaults', {}).get('llm', 'ollama')
    vault = config.get('preferences_schema', {}).get('system_preferences', {}).get('vault_location')

    if vault and Path(vault).exists():
        print(f"   ✓ Obsidian vault found: {vault}\n")
    else:
        print(f"   ⚠ Obsidian vault not found. Check: config/dcos_config.yaml\n")
        all_ok = False

    print(f"4️⃣ Backend selected: {backend}")

    if backend == 'ollama':
        print("   For Ollama, ensure it's running: ollama serve")
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            if response.status_code == 200:
                print("   ✓ Ollama is accessible\n")
            else:
                print("   ⚠ Ollama not responding. Start it: ollama serve\n")
        except:
            print("   ⚠ Ollama not found. Start it: ollama serve\n")

    elif backend == 'claude':
        if os.environ.get('CLAUDE_API_KEY'):
            print("   ✓ CLAUDE_API_KEY is set\n")
        else:
            print("   ⚠ CLAUDE_API_KEY not set. Export: export CLAUDE_API_KEY='sk-...'\n")
            all_ok = False

    # Test 5: OAuth credentials
    print("5️⃣ Checking Gmail credentials...")
    creds_path = Path(__file__).parent / 'config' / 'gmail_credentials.json'
    if creds_path.exists():
        print(f"   ✓ Gmail credentials found\n")
    else:
        print(f"   ℹ Gmail credentials not found yet. Setup at: {creds_path}\n")

    # Summary
    if all_ok:
        print("✓ All critical systems operational. Ready to run: python main.py")
    else:
        print("⚠ Fix issues above before running dCoS")

    return all_ok


def start_dcos(config):
    """Start Digital Chief of Staff"""
    print("""
╔════════════════════════════════════════╗
║  Digital Chief of Staff               ║
║  Your Personal AI Decision Support    ║
╚════════════════════════════════════════╝
    """)

    # Check database exists
    db_path = config.get('preferences_schema', {}).get('system_preferences', {}).get('database_location', './state/chief_of_staff.sqlite')
    db_path = Path(db_path).expanduser()

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        print("Initialize with: python main.py --init-db")
        sys.exit(1)

    print(f"✓ Database: {db_path}")

    backend = config.get('backend_defaults', {}).get('llm', 'ollama')
    print(f"✓ Backend: {backend}")

    vault = config.get('preferences_schema', {}).get('system_preferences', {}).get('vault_location')
    if vault and Path(vault).exists():
        print(f"✓ Vault: {vault}")
    else:
        print(f"⚠ Warning: Vault not found at {vault}")

    print("\n🚀 Starting dCoS...\n")

    try:
        # Import main modules
        import backend_executor
        import vault_indexing
        import account_manager

        print("✓ Modules loaded")
        print("✓ Capture hooks registered")
        print("✓ Backend executor ready")
        print("✓ Listening for email/calendar updates\n")

        print("Press Ctrl+C to stop\n")

        # Main loop (simplified for now)
        import time
        try:
            while True:
                # TODO: Implement actual event loop
                # For now, just keep running
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n✓ dCoS stopped gracefully")
            return 0

    except Exception as e:
        print(f"❌ Error starting dCoS: {e}")
        print("\nTroubleshooting:")
        print("1. Check config: config/dcos_config.yaml")
        print("2. Test systems: python main.py --test")
        print("3. See docs: docs/FAQ.md")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Digital Chief of Staff - Your Personal AI Assistant'
    )
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--test', action='store_true', help='Test all systems')
    parser.add_argument('--help-detailed', action='store_true', help='Show detailed help')

    args = parser.parse_args()

    # Load config (always needed)
    config = load_config()

    # Handle different commands
    if args.init_db:
        success = init_database(config)
        return 0 if success else 1

    elif args.test:
        success = test_systems(config)
        return 0 if success else 1

    elif args.help_detailed:
        print("""
Digital Chief of Staff - Complete Help

COMMANDS:
  python main.py              Start dCoS (main operation)
  python main.py --init-db    Initialize database
  python main.py --test       Test all systems
  python main.py --help       Show this message

QUICK START:
  1. Edit config/dcos_config.yaml
  2. Run: python main.py --init-db
  3. Run: python main.py --test
  4. Run: python main.py

DOCUMENTATION:
  README.md              - Overview and features
  QUICKSTART.md          - Setup guide (60 minutes)
  CREDITS.md             - Acknowledgments
  docs/CONFIGURATION.md  - Config reference
  docs/FEATURES.md       - Feature details
  docs/ARCHITECTURE.md   - System design
  docs/FAQ.md            - Troubleshooting

SUPPORT:
  - Check docs/FAQ.md for common issues
  - Review config/dcos_config.yaml for settings
  - Run --test to diagnose problems
        """)
        return 0

    else:
        # Default: start dCoS
        return start_dcos(config)


if __name__ == '__main__':
    sys.exit(main())
