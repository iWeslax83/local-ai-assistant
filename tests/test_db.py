import sqlite3
from core.db import init_db, get_db

def test_init_db_creates_all_tables(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(str(db_path))
    conn = sqlite3.connect(str(db_path))
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    expected = [
        "code_changes", "events", "expenses", "goals",
        "habit_logs", "habits", "messages", "moods",
        "notes", "preferences", "reminders", "tasks",
    ]
    assert tables == expected

def test_init_db_inserts_default_preferences(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(str(db_path))
    conn = sqlite3.connect(str(db_path))
    cursor = conn.execute("SELECT key, value FROM preferences ORDER BY key")
    prefs = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    assert prefs["morning_summary_time"] == "08:00"
    assert prefs["mood_check_time"] == "21:00"
    assert prefs["weekly_report_day"] == "sunday"
    assert prefs["weekly_report_time"] == "21:00"
    assert prefs["timezone"] == "Europe/Istanbul"

def test_get_db_returns_connection(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(str(db_path))
    conn = get_db(str(db_path))
    assert conn is not None
    conn.close()
