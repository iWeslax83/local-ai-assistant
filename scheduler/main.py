import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("scheduler")

from apscheduler.schedulers.blocking import BlockingScheduler
from core.db import get_db, init_db
from scheduler.jobs import (
    morning_summary_job, check_reminders_job, check_event_reminders_job,
    mood_check_job, weekly_report_job, monthly_report_job,
)

DB_PATH = "assistant.db"

def get_pref(key: str, default: str) -> str:
    conn = get_db(DB_PATH)
    try:
        row = conn.execute("SELECT value FROM preferences WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default
    finally:
        conn.close()

def main():
    init_db(DB_PATH)
    morning_time = get_pref("morning_summary_time", "08:00")
    mood_time = get_pref("mood_check_time", "21:00")
    report_day = get_pref("weekly_report_day", "sunday")
    report_time = get_pref("weekly_report_time", "21:00")

    morning_h, morning_m = morning_time.split(":")
    mood_h, mood_m = mood_time.split(":")
    report_h, report_m = report_time.split(":")

    scheduler = BlockingScheduler(timezone="Europe/Istanbul")
    scheduler.add_job(morning_summary_job, "cron", hour=int(morning_h), minute=int(morning_m), id="morning_summary")
    scheduler.add_job(check_reminders_job, "interval", minutes=1, id="check_reminders")
    scheduler.add_job(check_event_reminders_job, "interval", minutes=1, id="check_event_reminders")
    scheduler.add_job(mood_check_job, "cron", hour=int(mood_h), minute=int(mood_m), id="mood_check")
    scheduler.add_job(weekly_report_job, "cron", day_of_week=report_day[:3], hour=int(report_h), minute=int(report_m), id="weekly_report")
    scheduler.add_job(monthly_report_job, "cron", day="last", hour=int(report_h), minute=int(report_m), id="monthly_report")

    logger.info("Başlatıldı. Zamanlanmış görevler:")
    logger.info("  Sabah özeti: %s", morning_time)
    logger.info("  Hatırlatma kontrolü: her dakika")
    logger.info("  Ruh hali sorgusu: %s", mood_time)
    logger.info("  Haftalık rapor: %s %s", report_day, report_time)
    logger.info("  Aylık rapor: ayın son günü %s", report_time)
    scheduler.start()

if __name__ == "__main__":
    main()
