from core.intents.habits import handle_add_habit, handle_log_habit, handle_habit_status

def test_add_habit(db):
    result = handle_add_habit(db, {"name": "Su iç", "target": 8})
    assert "Su iç" in result
    row = db.execute("SELECT * FROM habits WHERE name = 'Su iç'").fetchone()
    assert row is not None
    assert row["target"] == 8
    assert row["active"] == 1

def test_log_habit(db):
    db.execute("INSERT INTO habits (name, target) VALUES ('Su iç', 8)")
    db.commit()
    result = handle_log_habit(db, {"name": "Su iç", "value": 2})
    assert "Su iç" in result
    row = db.execute("SELECT SUM(value) as total FROM habit_logs").fetchone()
    assert row["total"] == 2

def test_log_habit_not_found(db):
    result = handle_log_habit(db, {"name": "Olmayan", "value": 1})
    assert "bulunamadı" in result.lower() or "bulamadım" in result.lower()

def test_habit_status_empty(db):
    result = handle_habit_status(db, {})
    assert "alışkanlık yok" in result.lower() or "tanımlı" in result.lower()

def test_habit_status_with_data(db):
    db.execute("INSERT INTO habits (name, target) VALUES ('Su iç', 8)")
    db.commit()
    habit_id = db.execute("SELECT id FROM habits WHERE name = 'Su iç'").fetchone()["id"]
    db.execute("INSERT INTO habit_logs (habit_id, value) VALUES (?, 3)", (habit_id,))
    db.commit()
    result = handle_habit_status(db, {})
    assert "Su iç" in result
    assert "3" in result
