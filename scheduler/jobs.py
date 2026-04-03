import httpx
import sqlite3
from datetime import datetime
from core.db import get_db
from core.reports import build_morning_summary, build_weekly_report, build_monthly_report

BOT_URL = "http://localhost:3000/send"
DB_PATH = "assistant.db"

def _send_message(text: str) -> None:
    try:
        httpx.post(BOT_URL, json={"text": text}, timeout=30)
    except Exception as e:
        print(f"[Scheduler] Mesaj gönderilemedi: {e}")

def morning_summary_job() -> None:
    conn = get_db(DB_PATH)
    try:
        summary = build_morning_summary(conn)
        _send_message(summary)
    finally:
        conn.close()

def check_reminders_job() -> None:
    conn = get_db(DB_PATH)
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        reminders = conn.execute("SELECT id, message FROM reminders WHERE sent = 0 AND remind_at <= ?", (now,)).fetchall()
        for r in reminders:
            _send_message(f"🔔 Hatırlatma: **{r['message']}**")
            conn.execute("UPDATE reminders SET sent = 1 WHERE id = ?", (r["id"],))
        conn.commit()
    finally:
        conn.close()

def check_event_reminders_job() -> None:
    conn = get_db(DB_PATH)
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        events = conn.execute(
            "SELECT id, title, event_time FROM events WHERE remind_at IS NOT NULL AND remind_at <= ? AND reminder_sent = 0",
            (now,),
        ).fetchall()
        for e in events:
            _send_message(f"📅 Yaklaşan etkinlik: **{e['title']}**\n🕐 {e['event_time']}")
            conn.execute("UPDATE events SET reminder_sent = 1 WHERE id = ?", (e["id"],))
        conn.commit()
    finally:
        conn.close()

def mood_check_job() -> None:
    _send_message("🌙 Bugün nasıl geçti? Ruh halini ve kısa bir not paylaşır mısın?\n\nSeçenekler: harika / iyi / normal / kötü / berbat")

def weekly_report_job() -> None:
    conn = get_db(DB_PATH)
    try:
        report = build_weekly_report(conn)
        _send_message(report)
    finally:
        conn.close()

def monthly_report_job() -> None:
    conn = get_db(DB_PATH)
    try:
        report = build_monthly_report(conn)
        _send_message(report)
    finally:
        conn.close()
