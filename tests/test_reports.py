from core.reports import build_morning_summary, build_weekly_report, build_monthly_report

def test_morning_summary_empty(db):
    result = build_morning_summary(db)
    assert "Günaydın" in result

def test_morning_summary_with_tasks(db):
    db.execute("INSERT INTO tasks (title, priority, status, due_date) VALUES ('Test görevi', 'yüksek', 'bekliyor', DATE('now'))")
    db.commit()
    result = build_morning_summary(db)
    assert "Test görevi" in result

def test_morning_summary_with_events(db):
    db.execute("INSERT INTO events (title, event_time) VALUES ('Toplantı', DATETIME('now', '+2 hours'))")
    db.commit()
    result = build_morning_summary(db)
    assert "Toplantı" in result

def test_weekly_report(db):
    db.execute("INSERT INTO tasks (title, status) VALUES ('Biten görev', 'tamamlandı')")
    db.execute("INSERT INTO expenses (amount, category) VALUES (100, 'market')")
    db.execute("INSERT INTO moods (level) VALUES ('iyi')")
    db.commit()
    result = build_weekly_report(db)
    assert "Haftalık" in result

def test_monthly_report(db):
    db.execute("INSERT INTO tasks (title, status) VALUES ('Aylık görev', 'tamamlandı')")
    db.execute("INSERT INTO goals (title, target_value, current_value, unit, status) VALUES ('Test', 10, 5, 'adet', 'aktif')")
    db.commit()
    result = build_monthly_report(db)
    assert "Aylık" in result
