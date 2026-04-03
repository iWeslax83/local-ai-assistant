from core.intents.events import handle_add_event, handle_list_events

def test_add_event(db):
    result = handle_add_event(db, {"title": "Doktor randevusu", "event_time": "2026-04-04 15:00", "remind_at": "2026-04-04 14:00"})
    assert "Doktor randevusu" in result
    row = db.execute("SELECT * FROM events WHERE title = 'Doktor randevusu'").fetchone()
    assert row is not None
    assert row["remind_at"] == "2026-04-04 14:00"

def test_add_event_without_reminder(db):
    result = handle_add_event(db, {"title": "Toplantı", "event_time": "2026-04-04 09:30"})
    row = db.execute("SELECT * FROM events WHERE title = 'Toplantı'").fetchone()
    assert row["remind_at"] is None

def test_list_events_empty(db):
    result = handle_list_events(db, {})
    assert "etkinlik yok" in result.lower() or "boş" in result.lower()

def test_add_event_reminder_sent_defaults_false(db):
    from core.intents.events import handle_add_event
    handle_add_event(db, {"title": "Test", "event_time": "2026-04-04 15:00", "remind_at": "2026-04-04 14:00"})
    row = db.execute("SELECT reminder_sent FROM events WHERE title = 'Test'").fetchone()
    assert row["reminder_sent"] == 0

def test_list_events_with_data(db):
    db.execute("INSERT INTO events (title, event_time) VALUES ('Toplantı', '2026-04-04 09:30')")
    db.commit()
    result = handle_list_events(db, {})
    assert "Toplantı" in result
