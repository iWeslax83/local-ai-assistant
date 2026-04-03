import sqlite3
from datetime import date

def handle_add_task(conn: sqlite3.Connection, data: dict) -> str:
    title = data.get("title", "").strip()
    if not title:
        return "❌ Görev başlığı belirtilmedi."
    priority = data.get("priority", "normal")
    due_date = data.get("due_date")
    conn.execute("INSERT INTO tasks (title, priority, due_date) VALUES (?, ?, ?)", (title, priority, due_date))
    conn.commit()
    parts = [f"✅ Görev eklendi: **{title}**"]
    if due_date:
        parts.append(f"📅 Tarih: {due_date}")
    if priority != "normal":
        parts.append(f"⚡ Öncelik: {priority}")
    return "\n".join(parts)

def handle_list_tasks(conn: sqlite3.Connection, data: dict) -> str:
    rows = conn.execute(
        "SELECT id, title, priority, due_date FROM tasks WHERE status = 'bekliyor' ORDER BY "
        "CASE priority WHEN 'yüksek' THEN 1 WHEN 'normal' THEN 2 WHEN 'düşük' THEN 3 END, due_date ASC"
    ).fetchall()
    if not rows:
        return "📋 Bekleyen görev yok. Harika, herşey tamam! 🎉"
    priority_icons = {"yüksek": "🔴", "normal": "🟡", "düşük": "🟢"}
    lines = [f"📋 **Bekleyen Görevler ({len(rows)})**\n"]
    for i, row in enumerate(rows, 1):
        icon = priority_icons.get(row["priority"], "🟡")
        due = f" · 📅 {row['due_date']}" if row["due_date"] else ""
        lines.append(f"{i}. {icon} {row['title']}{due}")
    return "\n".join(lines)

def handle_complete_task(conn: sqlite3.Connection, data: dict) -> str:
    title = data.get("title", "").strip()
    if not title:
        return "❌ Hangi görevi tamamladığını belirtir misin?"
    cursor = conn.execute("UPDATE tasks SET status = 'tamamlandı' WHERE title LIKE ? AND status = 'bekliyor'", (f"%{title}%",))
    conn.commit()
    if cursor.rowcount == 0:
        return f"❌ '{title}' adında bekleyen bir görev bulunamadı."
    remaining = conn.execute("SELECT COUNT(*) as cnt FROM tasks WHERE status = 'bekliyor'").fetchone()["cnt"]
    return f"🎉 **{title}** tamamlandı olarak işaretlendi!\n📋 {remaining} görev kaldı."
