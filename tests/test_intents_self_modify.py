# tests/test_intents_self_modify.py
from unittest.mock import patch
from core.intents.self_modify import handle_modify_code, handle_confirm_code_change, handle_rollback_code


def test_modify_code_stores_pending(db):
    with patch("core.intents.self_modify._generate_code_plan", return_value="1. test.py - add feature"):
        result = handle_modify_code(db, {"request": "Haftalık özete harcama grafiği ekle"})
    assert "plan" in result.lower() or "onay" in result.lower()
    row = db.execute("SELECT * FROM code_changes WHERE status = 'beklemede'").fetchone()
    assert row is not None
    assert row["description"] == "Haftalık özete harcama grafiği ekle"
    assert row["plan"] is not None


def test_confirm_code_change_with_pending(db):
    db.execute(
        "INSERT INTO code_changes (description, plan, status) VALUES (?, ?, 'beklemede')",
        ("Test change", "1. test.py - change"),
    )
    db.commit()
    result = handle_confirm_code_change(db, {})
    assert "onaylandı" in result.lower()
    row = db.execute("SELECT status FROM code_changes ORDER BY id DESC LIMIT 1").fetchone()
    assert row["status"] == "uygulandı"


def test_confirm_code_change_no_pending(db):
    result = handle_confirm_code_change(db, {})
    assert "bekleyen" in result.lower() or "yok" in result.lower()


def test_rollback_code_no_changes(db):
    result = handle_rollback_code(db, {})
    assert "bulunamadı" in result.lower()


def test_rollback_code_with_change(db):
    db.execute(
        "INSERT INTO code_changes (description, files_changed, git_commit_hash, status) VALUES (?, ?, ?, ?)",
        ("Test change", '["test.py"]', "abc123", "uygulandı"),
    )
    db.commit()
    result = handle_rollback_code(db, {})
    assert "geri alındı" in result.lower()
    row = db.execute("SELECT status FROM code_changes WHERE git_commit_hash = 'abc123'").fetchone()
    assert row["status"] == "geri alındı"
