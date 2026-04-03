import sqlite3
from datetime import date, datetime, timedelta

def build_morning_summary(conn: sqlite3.Connection) -> str:
    today = date.today().isoformat()
    tasks = conn.execute(
        "SELECT title, priority FROM tasks WHERE status = 'bekliyor' AND (due_date = ? OR due_date IS NULL) "
        "ORDER BY CASE priority WHEN 'yüksek' THEN 1 WHEN 'normal' THEN 2 WHEN 'düşük' THEN 3 END",
        (today,),
    ).fetchall()
    events = conn.execute(
        "SELECT title, event_time FROM events WHERE DATE(event_time) = ? ORDER BY event_time", (today,),
    ).fetchall()
    habits = conn.execute("SELECT id, name, target FROM habits WHERE active = 1").fetchall()
    goals = conn.execute("SELECT title, current_value, target_value, unit FROM goals WHERE status = 'aktif'").fetchall()

    lines = ["☀️ **Günaydın!**\n"]
    if tasks:
        priority_icons = {"yüksek": "🔴", "normal": "🟡", "düşük": "🟢"}
        lines.append(f"📋 **{len(tasks)} görev** bugün:")
        for t in tasks:
            icon = priority_icons.get(t["priority"], "🟡")
            lines.append(f"  {icon} {t['title']}")
    else:
        lines.append("📋 Bugün görev yok. Rahat bir gün! 🎉")
    if events:
        lines.append(f"\n📅 **{len(events)} etkinlik:**")
        for e in events:
            time_str = e["event_time"].split(" ")[1] if " " in e["event_time"] else e["event_time"]
            lines.append(f"  🕐 {time_str} — {e['title']}")
    if habits:
        lines.append("\n✅ **Alışkanlıklar:**")
        for h in habits:
            lines.append(f"  • {h['name']} (hedef: {h['target']})")
    if goals:
        lines.append("\n🎯 **Hedefler:**")
        for g in goals:
            pct = int((g["current_value"] / g["target_value"]) * 100) if g["target_value"] > 0 else 0
            lines.append(f"  • {g['title']}: {g['current_value']}/{g['target_value']} {g['unit']} (%{pct})")
    lines.append("\nHangisine odaklanmak istersin?")
    return "\n".join(lines)

def build_weekly_report(conn: sqlite3.Connection) -> str:
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    completed = conn.execute("SELECT COUNT(*) as cnt FROM tasks WHERE status = 'tamamlandı' AND created_at >= ?", (week_ago,)).fetchone()["cnt"]
    expenses = conn.execute("SELECT category, SUM(amount) as total FROM expenses WHERE created_at >= ? GROUP BY category ORDER BY total DESC", (week_ago,)).fetchall()
    total_expense = sum(e["total"] for e in expenses) if expenses else 0
    moods = conn.execute("SELECT level, COUNT(*) as cnt FROM moods WHERE created_at >= ? GROUP BY level ORDER BY cnt DESC", (week_ago,)).fetchall()
    habits = conn.execute("SELECT id, name, target FROM habits WHERE active = 1").fetchall()

    lines = ["📊 **Haftalık Rapor**\n"]
    lines.append(f"✅ Tamamlanan görevler: **{completed}**")
    if expenses:
        cat_icons = {"market": "🛒", "ulaşım": "🚌", "yemek": "🍽️", "eğlence": "🎮", "fatura": "📄", "diğer": "📦"}
        lines.append(f"\n💰 Toplam harcama: **{total_expense:.0f} ₺**")
        for e in expenses:
            icon = cat_icons.get(e["category"], "📦")
            lines.append(f"  {icon} {e['category']}: {e['total']:.0f} ₺")
    if moods:
        mood_emojis = {"harika": "🤩", "iyi": "😊", "normal": "😐", "kötü": "😔", "berbat": "😢"}
        lines.append("\n😊 Ruh hali dağılımı:")
        for m in moods:
            emoji = mood_emojis.get(m["level"], "😐")
            lines.append(f"  {emoji} {m['level']}: {m['cnt']} gün")
    if habits:
        lines.append("\n🔥 Alışkanlık serileri:")
        for h in habits:
            streak = conn.execute(
                "SELECT COUNT(DISTINCT DATE(logged_at)) as days FROM habit_logs WHERE habit_id = ? AND logged_at >= ?",
                (h["id"], week_ago),
            ).fetchone()["days"]
            lines.append(f"  • {h['name']}: {streak}/7 gün")
    return "\n".join(lines)

def build_monthly_report(conn: sqlite3.Connection) -> str:
    month_start = date.today().replace(day=1).isoformat()
    completed = conn.execute("SELECT COUNT(*) as cnt FROM tasks WHERE status = 'tamamlandı' AND created_at >= ?", (month_start,)).fetchone()["cnt"]
    expenses = conn.execute("SELECT category, SUM(amount) as total FROM expenses WHERE created_at >= ? GROUP BY category ORDER BY total DESC", (month_start,)).fetchall()
    total_expense = sum(e["total"] for e in expenses) if expenses else 0
    goals = conn.execute("SELECT title, target_value, current_value, unit, status FROM goals").fetchall()
    moods = conn.execute("SELECT level, COUNT(*) as cnt FROM moods WHERE created_at >= ? GROUP BY level", (month_start,)).fetchall()

    lines = ["📊 **Aylık Rapor**\n"]
    lines.append(f"✅ Tamamlanan görevler: **{completed}**")
    lines.append(f"💰 Toplam harcama: **{total_expense:.0f} ₺**")
    if goals:
        lines.append("\n🎯 Hedef durumu:")
        for g in goals:
            status_icon = "✅" if g["status"] == "tamamlandı" else "🔄"
            lines.append(f"  {status_icon} {g['title']}: {g['current_value']}/{g['target_value']} {g['unit']}")
    if moods:
        level_scores = {"harika": 5, "iyi": 4, "normal": 3, "kötü": 2, "berbat": 1}
        total_moods = sum(m["cnt"] for m in moods)
        avg = sum(level_scores.get(m["level"], 3) * m["cnt"] for m in moods) / total_moods
        avg_label = "harika" if avg >= 4.5 else "iyi" if avg >= 3.5 else "normal" if avg >= 2.5 else "kötü" if avg >= 1.5 else "berbat"
        lines.append(f"\n😊 Ortalama ruh hali: **{avg_label}** ({avg:.1f}/5)")
    return "\n".join(lines)
