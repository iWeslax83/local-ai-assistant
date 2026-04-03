import sqlite3

def handle_add_note(conn: sqlite3.Connection, data: dict) -> str:
    content = data.get("content", "").strip()
    if not content:
        return "❌ Not içeriği belirtilmedi."
    tag = data.get("tag")
    conn.execute("INSERT INTO notes (content, tag) VALUES (?, ?)", (content, tag))
    conn.commit()
    tag_str = f" 🏷️ Etiket: {tag}" if tag else ""
    preview = content[:50] + "..." if len(content) > 50 else content
    return f"📝 Not kaydedildi: {preview}{tag_str}"

def handle_search_notes(conn: sqlite3.Connection, data: dict) -> str:
    query = data.get("query", "").strip()
    if not query:
        return "❌ Ne aramak istediğini belirtir misin?"
    rows = conn.execute("SELECT content, tag, created_at FROM notes WHERE content LIKE ? ORDER BY created_at DESC", (f"%{query}%",)).fetchall()
    if not rows:
        return f"🔍 '{query}' ile ilgili not bulunamadı."
    lines = [f"🔍 **'{query}' ile ilgili notlar ({len(rows)})**\n"]
    for row in rows:
        tag_str = f" [{row['tag']}]" if row["tag"] else ""
        lines.append(f"📝 {row['content']}{tag_str}")
    return "\n".join(lines)
