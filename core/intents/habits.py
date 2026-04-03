import sqlite3
from datetime import date

def handle_add_habit(conn: sqlite3.Connection, data: dict) -> str:
    name = data.get("name", "").strip()
    if not name:
        return "❌ Alışkanlık adı belirtilmedi."
    target = data.get("target", 1)
    conn.execute("INSERT INTO habits (name, target) VALUES (?, ?)", (name, target))
    conn.commit()
    return f"✅ Alışkanlık eklendi: **{name}**\n🎯 Günlük hedef: {target}"

def handle_log_habit(conn: sqlite3.Connection, data: dict) -> str:
    name = data.get("name", "").strip()
    value = data.get("value", 1)
    habit = conn.execute("SELECT id, name, target FROM habits WHERE name LIKE ? AND active = 1", (f"%{name}%",)).fetchone()
    if not habit:
        return f"❌ '{name}' adında aktif bir alışkanlık bulunamadı."
    conn.execute("INSERT INTO habit_logs (habit_id, value) VALUES (?, ?)", (habit["id"], value))
    conn.commit()
    today = date.today().isoformat()
    total = conn.execute(
        "SELECT COALESCE(SUM(value), 0) as total FROM habit_logs WHERE habit_id = ? AND DATE(logged_at) = ?",
        (habit["id"], today),
    ).fetchone()["total"]
    return f"✅ **{habit['name']}**: {total}/{habit['target']} bugün"

def handle_habit_status(conn: sqlite3.Connection, data: dict) -> str:
    habits = conn.execute("SELECT id, name, target FROM habits WHERE active = 1 ORDER BY name").fetchall()
    if not habits:
        return "📊 Tanımlı aktif alışkanlık yok."
    today = date.today().isoformat()
    lines = ["✅ **Alışkanlık Durumu**\n"]
    for h in habits:
        total = conn.execute(
            "SELECT COALESCE(SUM(value), 0) as total FROM habit_logs WHERE habit_id = ? AND DATE(logged_at) = ?",
            (h["id"], today),
        ).fetchone()["total"]
        streak = _calculate_streak(conn, h["id"], h["target"])
        streak_str = f" · 🔥 {streak} gün seri" if streak > 0 else ""
        lines.append(f"• {h['name']}: {total}/{h['target']}{streak_str}")
    return "\n".join(lines)

def _calculate_streak(conn: sqlite3.Connection, habit_id: int, target: int) -> int:
    rows = conn.execute(
        "SELECT DATE(logged_at) as day, SUM(value) as total FROM habit_logs WHERE habit_id = ? GROUP BY DATE(logged_at) ORDER BY day DESC",
        (habit_id,),
    ).fetchall()
    streak = 0
    for row in rows:
        if row["total"] >= target:
            streak += 1
        else:
            break
    return streak
