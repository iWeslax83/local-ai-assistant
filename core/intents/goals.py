import sqlite3
from datetime import date

def handle_add_goal(conn: sqlite3.Connection, data: dict) -> str:
    title = data.get("title", "").strip()
    if not title:
        return "❌ Hedef başlığı belirtilmedi."
    target_value = data.get("target_value", 1)
    unit = data.get("unit", "adet")
    deadline = data.get("deadline")
    conn.execute("INSERT INTO goals (title, target_value, unit, deadline) VALUES (?, ?, ?, ?)", (title, target_value, unit, deadline))
    conn.commit()
    deadline_str = f"\n📅 Bitiş: {deadline}" if deadline else ""
    return f"🎯 Hedef eklendi: **{title}**\n📊 Hedef: {target_value} {unit}{deadline_str}"

def handle_update_goal(conn: sqlite3.Connection, data: dict) -> str:
    title = data.get("title", "").strip()
    value = data.get("value", 1)
    goal = conn.execute("SELECT id, title, target_value, current_value, unit FROM goals WHERE title LIKE ? AND status = 'aktif'", (f"%{title}%",)).fetchone()
    if not goal:
        return f"❌ '{title}' adında aktif bir hedef bulunamadı."
    new_value = goal["current_value"] + value
    new_status = "tamamlandı" if new_value >= goal["target_value"] else "aktif"
    conn.execute("UPDATE goals SET current_value = ?, status = ? WHERE id = ?", (new_value, new_status, goal["id"]))
    conn.commit()
    if new_status == "tamamlandı":
        return f"🎉🎉 Tebrikler! **{goal['title']}** hedefini tamamladın! ({new_value}/{goal['target_value']} {goal['unit']})"
    remaining = goal["target_value"] - new_value
    return f"📊 **{goal['title']}**: {new_value}/{goal['target_value']} {goal['unit']}\n💪 {remaining} {goal['unit']} kaldı!"

def handle_goal_status(conn: sqlite3.Connection, data: dict) -> str:
    goals = conn.execute("SELECT title, target_value, current_value, unit, deadline, status FROM goals WHERE status = 'aktif' ORDER BY deadline ASC").fetchall()
    if not goals:
        return "🎯 Aktif hedef yok. Yeni bir hedef belirlemek ister misin?"
    lines = ["🎯 **Aktif Hedefler**\n"]
    for g in goals:
        pct = int((g["current_value"] / g["target_value"]) * 100) if g["target_value"] > 0 else 0
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
        deadline_str = ""
        if g["deadline"]:
            days_left = (date.fromisoformat(g["deadline"]) - date.today()).days
            deadline_str = f" · ⏳ {days_left} gün kaldı" if days_left > 0 else " · ⚠️ Süre doldu!"
        lines.append(f"• **{g['title']}**: {g['current_value']}/{g['target_value']} {g['unit']} [{bar}] %{pct}{deadline_str}")
    return "\n".join(lines)
