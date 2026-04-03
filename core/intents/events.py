import sqlite3

def handle_add_event(conn: sqlite3.Connection, data: dict) -> str:
    title = data.get("title", "").strip()
    if not title:
        return "❌ Etkinlik başlığı belirtilmedi."
    event_time = data.get("event_time")
    if not event_time:
        return "❌ Etkinlik zamanı belirtilmedi."
    remind_at = data.get("remind_at")
    conn.execute("INSERT INTO events (title, event_time, remind_at) VALUES (?, ?, ?)", (title, event_time, remind_at))
    conn.commit()
    parts = [f"📅 Etkinlik eklendi: **{title}**", f"🕐 Zaman: {event_time}"]
    if remind_at:
        parts.append(f"🔔 Hatırlatma: {remind_at}")
    return "\n".join(parts)

def handle_list_events(conn: sqlite3.Connection, data: dict) -> str:
    rows = conn.execute("SELECT title, event_time FROM events ORDER BY event_time ASC").fetchall()
    if not rows:
        return "📅 Yaklaşan etkinlik yok."
    lines = [f"📅 **Etkinlikler ({len(rows)})**\n"]
    for row in rows:
        lines.append(f"• {row['title']} — {row['event_time']}")
    return "\n".join(lines)
