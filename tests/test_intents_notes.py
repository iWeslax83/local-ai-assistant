from core.intents.notes import handle_add_note, handle_search_notes

def test_add_note(db):
    result = handle_add_note(db, {"content": "Ali'nin telefonu: 0532 123 4567", "tag": "kişiler"})
    assert "Ali" in result
    row = db.execute("SELECT * FROM notes WHERE tag = 'kişiler'").fetchone()
    assert row is not None
    assert "0532" in row["content"]

def test_add_note_without_tag(db):
    result = handle_add_note(db, {"content": "Önemli bir not"})
    row = db.execute("SELECT * FROM notes WHERE content LIKE '%Önemli%'").fetchone()
    assert row is not None
    assert row["tag"] is None

def test_search_notes(db):
    db.execute("INSERT INTO notes (content, tag) VALUES ('Ali tel: 0532', 'kişiler')")
    db.execute("INSERT INTO notes (content, tag) VALUES ('Toplantı notları', 'iş')")
    db.commit()
    result = handle_search_notes(db, {"query": "Ali"})
    assert "Ali" in result
    assert "Toplantı" not in result

def test_search_notes_no_results(db):
    result = handle_search_notes(db, {"query": "olmayan"})
    assert "bulunamadı" in result.lower() or "bulamadım" in result.lower()
