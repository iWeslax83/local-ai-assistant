import json
from core.intents.self_modify import handle_modify_code, handle_rollback_code

def test_modify_code_stores_pending(db):
    result = handle_modify_code(db, {"request": "Haftalık özete harcama grafiği ekle"})
    assert "onay" in result.lower() or "plan" in result.lower()

def test_rollback_code_no_changes(db):
    result = handle_rollback_code(db, {})
    assert "değişiklik yok" in result.lower() or "bulunamadı" in result.lower()

def test_rollback_code_with_change(db):
    db.execute(
        "INSERT INTO code_changes (description, files_changed, git_commit_hash, status) VALUES (?, ?, ?, ?)",
        ("Test change", '["test.py"]', "abc123", "uygulandı"),
    )
    db.commit()
    result = handle_rollback_code(db, {})
    assert "geri alındı" in result.lower() or "rollback" in result.lower()
    row = db.execute("SELECT status FROM code_changes WHERE git_commit_hash = 'abc123'").fetchone()
    assert row["status"] == "geri alındı"
