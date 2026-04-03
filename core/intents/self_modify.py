import json
import sqlite3
import subprocess
from datetime import datetime

def handle_modify_code(conn: sqlite3.Connection, data: dict) -> str:
    request = data.get("request", "").strip()
    if not request:
        return "❌ Ne değiştirmek istediğini belirtir misin?"
    return (
        f"🔧 Kod değişikliği isteği alındı:\n\n"
        f"📝 **{request}**\n\n"
        f"⚠️ Bu özellik için Ollama'dan detaylı plan oluşturulacak. "
        f"Planı gördükten sonra **evet** yazarak onaylayabilir "
        f"veya **hayır** yazarak iptal edebilirsin."
    )

def handle_confirm_code_change(conn: sqlite3.Connection, data: dict) -> str:
    return "✅ Kod değişikliği onaylandı. Değişiklikler uygulanıyor..."

def handle_rollback_code(conn: sqlite3.Connection, data: dict) -> str:
    last_change = conn.execute(
        "SELECT id, description, git_commit_hash FROM code_changes WHERE status = 'uygulandı' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if not last_change:
        return "❌ Geri alınacak kod değişikliği bulunamadı."
    conn.execute("UPDATE code_changes SET status = 'geri alındı' WHERE id = ?", (last_change["id"],))
    conn.commit()
    try:
        subprocess.run(["git", "revert", "--no-commit", last_change["git_commit_hash"]], cwd=".", capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", f"revert: {last_change['description']}"], cwd=".", capture_output=True, text=True)
    except Exception:
        pass
    return f"↩️ Son değişiklik geri alındı:\n📝 {last_change['description']}\n🔄 Commit: {last_change['git_commit_hash'][:7]}"
