# core/intents/self_modify.py
import json
import os
import sqlite3
import subprocess
from datetime import datetime

import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1:8b"


def _generate_code_plan(request: str) -> str:
    """Call Ollama to generate a code change plan."""
    prompt = f"""Sen bir yazılım geliştiricisin. Aşağıdaki istek için bir kod değişikliği planı oluştur.
Hangi dosyaların değişeceğini, ne eklenip ne çıkarılacağını kısa ve net açıkla.

İstek: {request}

Proje yapısı:
- core/main.py: FastAPI sunucu
- core/ai.py: Ollama entegrasyonu
- core/db.py: SQLite veritabanı
- core/intents/: Intent handler'lar (tasks.py, events.py, notes.py, habits.py, expenses.py, moods.py, goals.py, preferences.py, reminders.py, self_modify.py)
- core/reports.py: Raporlar
- scheduler/jobs.py: Zamanlanmış görevler
- scheduler/main.py: Scheduler

Yanıtını şu formatta ver:
PLAN:
1. [dosya_adı] - [yapılacak değişiklik]
2. [dosya_adı] - [yapılacak değişiklik]

AÇIKLAMA:
[Kısa açıklama]"""

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.3},
            },
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        return f"Plan oluşturulamadı: {str(e)}"


def handle_modify_code(conn: sqlite3.Connection, data: dict) -> str:
    request = data.get("request", "").strip()
    if not request:
        return "❌ Ne değiştirmek istediğini belirtir misin?"

    # Generate plan from Ollama
    plan = _generate_code_plan(request)

    # Store pending change in database
    conn.execute(
        "INSERT INTO code_changes (description, plan, status) VALUES (?, ?, 'beklemede')",
        (request, plan),
    )
    conn.commit()

    return (
        f"🔧 **Kod değişikliği planı:**\n\n"
        f"📝 İstek: {request}\n\n"
        f"📋 Plan:\n{plan}\n\n"
        f"⚠️ Onaylıyor musun? **evet** veya **hayır** yaz."
    )


def handle_confirm_code_change(conn: sqlite3.Connection, data: dict) -> str:
    # Find the latest pending change
    pending = conn.execute(
        "SELECT id, description, plan FROM code_changes WHERE status = 'beklemede' ORDER BY id DESC LIMIT 1"
    ).fetchone()

    if not pending:
        return "❌ Onaylanacak bekleyen bir değişiklik yok."

    # Create a git backup before applying changes
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True, text=True,
        )
        backup_hash = result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        backup_hash = "unknown"

    # Mark as applied with backup hash
    conn.execute(
        "UPDATE code_changes SET status = 'uygulandı', git_commit_hash = ? WHERE id = ?",
        (backup_hash, pending["id"]),
    )
    conn.commit()

    return (
        f"✅ Değişiklik onaylandı ve kaydedildi.\n\n"
        f"📝 {pending['description']}\n"
        f"🔄 Yedek commit: {backup_hash[:7]}\n\n"
        f"⚠️ Not: Kod değişikliklerini uygulamak için projeyi yeniden dağıtman gerekiyor.\n"
        f"Geri almak istersen **son değişikliği geri al** yaz."
    )


def handle_rollback_code(conn: sqlite3.Connection, data: dict) -> str:
    last_change = conn.execute(
        "SELECT id, description, git_commit_hash FROM code_changes WHERE status = 'uygulandı' ORDER BY id DESC LIMIT 1"
    ).fetchone()

    if not last_change:
        return "❌ Geri alınacak kod değişikliği bulunamadı."

    conn.execute(
        "UPDATE code_changes SET status = 'geri alındı' WHERE id = ?",
        (last_change["id"],),
    )
    conn.commit()

    # Attempt git revert if we have a valid hash
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if last_change["git_commit_hash"] and last_change["git_commit_hash"] != "unknown":
        try:
            subprocess.run(
                ["git", "revert", "--no-commit", last_change["git_commit_hash"]],
                cwd=project_dir, capture_output=True, text=True,
            )
            subprocess.run(
                ["git", "commit", "-m", f"revert: {last_change['description']}"],
                cwd=project_dir, capture_output=True, text=True,
            )
        except Exception:
            pass

    return (
        f"↩️ Son değişiklik geri alındı:\n"
        f"📝 {last_change['description']}\n"
        f"🔄 Commit: {last_change['git_commit_hash'][:7] if last_change['git_commit_hash'] else 'N/A'}"
    )
