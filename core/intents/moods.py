import sqlite3

MOOD_EMOJIS = {"harika": "🤩", "iyi": "😊", "normal": "😐", "kötü": "😔", "berbat": "😢"}

def handle_log_mood(conn: sqlite3.Connection, data: dict) -> str:
    level = data.get("level", "").strip().lower()
    valid_levels = ["harika", "iyi", "normal", "kötü", "berbat"]
    if level not in valid_levels:
        return f"❌ Ruh hali seviyesi geçersiz. Seçenekler: {', '.join(valid_levels)}"
    journal = data.get("journal")
    conn.execute("INSERT INTO moods (level, journal) VALUES (?, ?)", (level, journal))
    conn.commit()
    emoji = MOOD_EMOJIS.get(level, "😐")
    response = f"{emoji} Ruh halin kaydedildi: **{level}**"
    if journal:
        response += f"\n📝 {journal}"
    return response

def handle_mood_trend(conn: sqlite3.Connection, data: dict) -> str:
    period = data.get("period", "week")

    if period == "month":
        limit = 30
        period_label = "Son 30 Gün"
    elif period == "year":
        limit = 365
        period_label = "Son 1 Yıl"
    else:  # week (default)
        limit = 7
        period_label = "Son 7 Gün"

    rows = conn.execute(
        "SELECT level, journal, DATE(created_at) as day FROM moods ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    if not rows:
        return "😊 Henüz ruh hali kaydı yok."
    lines = [f"😊 **Ruh Hali Trendi — {period_label}**\n"]
    for row in rows:
        emoji = MOOD_EMOJIS.get(row["level"], "😐")
        journal_str = f" — {row['journal']}" if row["journal"] else ""
        lines.append(f"{emoji} {row['day']}: {row['level']}{journal_str}")
    level_scores = {"harika": 5, "iyi": 4, "normal": 3, "kötü": 2, "berbat": 1}
    avg = sum(level_scores.get(r["level"], 3) for r in rows) / len(rows)
    avg_label = "harika" if avg >= 4.5 else "iyi" if avg >= 3.5 else "normal" if avg >= 2.5 else "kötü" if avg >= 1.5 else "berbat"
    lines.append(f"\n📊 Genel ortalama: **{avg_label}** ({avg:.1f}/5)")
    return "\n".join(lines)
