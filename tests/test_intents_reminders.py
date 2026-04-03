from core.intents.reminders import handle_add_reminder

def test_add_reminder(db):
    result = handle_add_reminder(db, {"message": "İlacı iç", "remind_at": "2026-04-03 16:00"})
    assert "İlacı iç" in result
    row = db.execute("SELECT * FROM reminders WHERE message = 'İlacı iç'").fetchone()
    assert row is not None
    assert row["sent"] == 0

def test_add_reminder_missing_time(db):
    result = handle_add_reminder(db, {"message": "Test"})
    assert "zaman" in result.lower() or "belirt" in result.lower()
