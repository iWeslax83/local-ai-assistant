from core.intents.moods import handle_log_mood, handle_mood_trend

def test_log_mood(db):
    result = handle_log_mood(db, {"level": "iyi", "journal": "Güzel bir gün geçirdim"})
    assert "iyi" in result.lower()
    row = db.execute("SELECT * FROM moods").fetchone()
    assert row["level"] == "iyi"
    assert row["journal"] == "Güzel bir gün geçirdim"

def test_log_mood_without_journal(db):
    result = handle_log_mood(db, {"level": "normal"})
    row = db.execute("SELECT * FROM moods").fetchone()
    assert row["journal"] is None

def test_mood_trend_empty(db):
    result = handle_mood_trend(db, {})
    assert "kayıt yok" in result.lower() or "henüz" in result.lower()

def test_mood_trend_with_data(db):
    db.execute("INSERT INTO moods (level, journal) VALUES ('harika', 'Süper gün')")
    db.execute("INSERT INTO moods (level, journal) VALUES ('iyi', 'Normal gün')")
    db.execute("INSERT INTO moods (level, journal) VALUES ('kötü', 'Zor gün')")
    db.commit()
    result = handle_mood_trend(db, {})
    assert "harika" in result.lower() or "iyi" in result.lower()

def test_mood_trend_monthly(db):
    db.execute("INSERT INTO moods (level, journal) VALUES ('iyi', 'Test')")
    db.commit()
    result = handle_mood_trend(db, {"period": "month"})
    assert "30 Gün" in result
