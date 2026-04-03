from core.intents.expenses import handle_add_expense, handle_expense_summary

def test_add_expense(db):
    result = handle_add_expense(db, {"amount": 450, "category": "market", "description": "Haftalık alışveriş"})
    assert "450" in result
    row = db.execute("SELECT * FROM expenses").fetchone()
    assert row["amount"] == 450
    assert row["category"] == "market"

def test_add_expense_default_category(db):
    result = handle_add_expense(db, {"amount": 100, "description": "Bir şey"})
    row = db.execute("SELECT category FROM expenses").fetchone()
    assert row["category"] == "diğer"

def test_expense_summary(db):
    db.execute("INSERT INTO expenses (amount, category, description) VALUES (450, 'market', 'Alışveriş')")
    db.execute("INSERT INTO expenses (amount, category, description) VALUES (50, 'ulaşım', 'Otobüs')")
    db.execute("INSERT INTO expenses (amount, category, description) VALUES (200, 'market', 'Manav')")
    db.commit()
    result = handle_expense_summary(db, {"period": "month"})
    assert "700" in result
    assert "market" in result.lower()

def test_expense_summary_empty(db):
    result = handle_expense_summary(db, {})
    assert "harcama yok" in result.lower() or "0" in result
