import sqlite3

def handle_add_reminder(conn: sqlite3.Connection, data: dict) -> str:
    message = data.get("message", "").strip()
    if not message:
        return "❌ Hatırlatma mesajı belirtilmedi."
    remind_at = data.get("remind_at")
    if not remind_at:
        return "❌ Hatırlatma zamanı belirtilmedi."
    conn.execute("INSERT INTO reminders (message, remind_at) VALUES (?, ?)", (message, remind_at))
    conn.commit()
    return f"🔔 Hatırlatma kuruldu: **{message}**\n⏰ Zaman: {remind_at}"
