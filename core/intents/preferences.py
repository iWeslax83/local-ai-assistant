import sqlite3
from datetime import datetime

VALID_KEYS = {
    "morning_summary_time": "Sabah özeti zamanı",
    "mood_check_time": "Ruh hali sorgusu zamanı",
    "weekly_report_day": "Haftalık rapor günü",
    "weekly_report_time": "Haftalık rapor zamanı",
    "timezone": "Zaman dilimi",
}

def handle_update_preference(conn: sqlite3.Connection, data: dict) -> str:
    key = data.get("key", "").strip()
    value = data.get("value", "").strip()
    if key not in VALID_KEYS:
        valid_list = ", ".join(VALID_KEYS.keys())
        return f"❌ Geçersiz ayar anahtarı. Geçerli anahtarlar: {valid_list}"
    if not value:
        return "❌ Ayar değeri belirtilmedi."
    old = conn.execute("SELECT value FROM preferences WHERE key = ?", (key,)).fetchone()
    old_value = old["value"] if old else "yok"
    conn.execute("INSERT OR REPLACE INTO preferences (key, value, updated_at) VALUES (?, ?, ?)", (key, value, datetime.now().isoformat()))
    conn.commit()
    label = VALID_KEYS[key]
    return f"⚙️ **{label}** güncellendi\n📝 Önceki: {old_value}\n✅ Yeni: {value}"
