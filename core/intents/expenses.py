import sqlite3
from datetime import datetime

def handle_add_expense(conn: sqlite3.Connection, data: dict) -> str:
    amount = data.get("amount")
    if not amount:
        return "❌ Harcama miktarı belirtilmedi."
    category = data.get("category", "diğer")
    description = data.get("description", "")
    conn.execute("INSERT INTO expenses (amount, category, description) VALUES (?, ?, ?)", (amount, category, description))
    conn.commit()
    cat_icons = {"market": "🛒", "ulaşım": "🚌", "yemek": "🍽️", "eğlence": "🎮", "fatura": "📄", "diğer": "📦"}
    icon = cat_icons.get(category, "📦")
    return f"💰 Harcama kaydedildi: **{amount} ₺** {icon} {category}\n📝 {description}" if description else f"💰 Harcama kaydedildi: **{amount} ₺** {icon} {category}"

def handle_expense_summary(conn: sqlite3.Connection, data: dict) -> str:
    now = datetime.now()
    month_start = now.strftime("%Y-%m-01")
    rows = conn.execute(
        "SELECT category, SUM(amount) as total FROM expenses WHERE created_at >= ? GROUP BY category ORDER BY total DESC",
        (month_start,),
    ).fetchall()
    if not rows:
        return "💰 Bu ay henüz harcama yok."
    grand_total = sum(row["total"] for row in rows)
    cat_icons = {"market": "🛒", "ulaşım": "🚌", "yemek": "🍽️", "eğlence": "🎮", "fatura": "📄", "diğer": "📦"}
    lines = [f"💰 **Bu Ay Harcama Özeti**\n", f"**Toplam: {grand_total:.0f} ₺**\n"]
    for row in rows:
        icon = cat_icons.get(row["category"], "📦")
        lines.append(f"{icon} {row['category']}: {row['total']:.0f} ₺")
    return "\n".join(lines)
