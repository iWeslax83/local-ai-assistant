from core.intents.tasks import handle_add_task, handle_list_tasks, handle_complete_task

def test_add_task(db):
    result = handle_add_task(db, {"title": "Market alışverişi", "priority": "normal", "due_date": "2026-04-03"})
    assert "Market alışverişi" in result
    row = db.execute("SELECT * FROM tasks WHERE title = 'Market alışverişi'").fetchone()
    assert row is not None
    assert row["priority"] == "normal"
    assert row["status"] == "bekliyor"

def test_add_task_defaults(db):
    result = handle_add_task(db, {"title": "Basit görev"})
    row = db.execute("SELECT * FROM tasks WHERE title = 'Basit görev'").fetchone()
    assert row["priority"] == "normal"
    assert row["due_date"] is None

def test_list_tasks_empty(db):
    result = handle_list_tasks(db, {})
    assert "görev yok" in result.lower() or "boş" in result.lower()

def test_list_tasks_with_data(db):
    db.execute("INSERT INTO tasks (title, priority, status) VALUES ('Görev 1', 'yüksek', 'bekliyor')")
    db.execute("INSERT INTO tasks (title, priority, status) VALUES ('Görev 2', 'normal', 'bekliyor')")
    db.commit()
    result = handle_list_tasks(db, {})
    assert "Görev 1" in result
    assert "Görev 2" in result

def test_complete_task(db):
    db.execute("INSERT INTO tasks (title, status) VALUES ('Raporu bitir', 'bekliyor')")
    db.commit()
    result = handle_complete_task(db, {"title": "Raporu bitir"})
    assert "tamamlandı" in result.lower()
    row = db.execute("SELECT status FROM tasks WHERE title = 'Raporu bitir'").fetchone()
    assert row["status"] == "tamamlandı"

def test_complete_task_not_found(db):
    result = handle_complete_task(db, {"title": "Olmayan görev"})
    assert "bulunamadı" in result.lower() or "bulamadım" in result.lower()
