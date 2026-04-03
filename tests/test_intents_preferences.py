from core.intents.preferences import handle_update_preference

def test_update_preference(db):
    result = handle_update_preference(db, {"key": "morning_summary_time", "value": "07:30"})
    assert "07:30" in result
    row = db.execute("SELECT value FROM preferences WHERE key = 'morning_summary_time'").fetchone()
    assert row["value"] == "07:30"

def test_update_preference_invalid_key(db):
    result = handle_update_preference(db, {"key": "nonexistent_key", "value": "test"})
    assert "geçersiz" in result.lower() or "bulunamadı" in result.lower()
