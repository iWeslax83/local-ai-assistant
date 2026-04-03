#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Yerel AI Asistan başlatılıyor..."
echo ""

if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama bulunamadı. Kurulum: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "🦙 Ollama başlatılıyor..."
    ollama serve &
    sleep 3
fi

if ! ollama list | grep -q "llama3.1:8b"; then
    echo "📥 Llama 3.1 8B modeli indiriliyor..."
    ollama pull llama3.1:8b
fi

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "🧠 Core API başlatılıyor..."
cd core
uvicorn main:app --host 0.0.0.0 --port 8000 &
CORE_PID=$!
cd "$SCRIPT_DIR"
sleep 2

echo "⏰ Scheduler başlatılıyor..."
python scheduler/main.py &
SCHEDULER_PID=$!

echo "💬 WhatsApp Bot başlatılıyor..."
cd bot
npm start &
BOT_PID=$!
cd "$SCRIPT_DIR"

echo ""
echo "✅ Tüm servisler başlatıldı!"
echo "   🧠 Core API:   PID $CORE_PID (port 8000)"
echo "   ⏰ Scheduler:  PID $SCHEDULER_PID"
echo "   💬 WhatsApp:   PID $BOT_PID (port 3000)"
echo ""
echo "📱 WhatsApp QR kodunu tarayın..."
echo "   Durdurmak için: kill $CORE_PID $SCHEDULER_PID $BOT_PID"

echo "$CORE_PID $SCHEDULER_PID $BOT_PID" > .pids

wait
