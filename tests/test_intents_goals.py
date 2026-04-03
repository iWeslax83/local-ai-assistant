from core.intents.goals import handle_add_goal, handle_update_goal, handle_goal_status

def test_add_goal(db):
    result = handle_add_goal(db, {"title": "Kitap oku", "target_value": 10, "unit": "kitap", "deadline": "2026-04-30"})
    assert "Kitap oku" in result
    row = db.execute("SELECT * FROM goals WHERE title = 'Kitap oku'").fetchone()
    assert row["target_value"] == 10
    assert row["current_value"] == 0
    assert row["status"] == "aktif"

def test_update_goal(db):
    db.execute("INSERT INTO goals (title, target_value, current_value, unit, status) VALUES ('Kitap oku', 10, 3, 'kitap', 'aktif')")
    db.commit()
    result = handle_update_goal(db, {"title": "Kitap oku", "value": 2})
    assert "5" in result
    row = db.execute("SELECT current_value FROM goals WHERE title = 'Kitap oku'").fetchone()
    assert row["current_value"] == 5

def test_update_goal_completes(db):
    db.execute("INSERT INTO goals (title, target_value, current_value, unit, status) VALUES ('Kitap oku', 10, 9, 'kitap', 'aktif')")
    db.commit()
    result = handle_update_goal(db, {"title": "Kitap oku", "value": 1})
    row = db.execute("SELECT status FROM goals WHERE title = 'Kitap oku'").fetchone()
    assert row["status"] == "tamamlandı"

def test_goal_status(db):
    db.execute("INSERT INTO goals (title, target_value, current_value, unit, deadline, status) VALUES ('Kitap oku', 10, 6, 'kitap', '2026-04-30', 'aktif')")
    db.commit()
    result = handle_goal_status(db, {})
    assert "Kitap oku" in result
    assert "6" in result
    assert "10" in result

def test_goal_status_empty(db):
    result = handle_goal_status(db, {})
    assert "hedef yok" in result.lower() or "henüz" in result.lower()
