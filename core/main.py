from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date

from core.db import init_db, get_db
from core.ai import chat
from core.intents import dispatch_intent

DB_PATH = "assistant.db"

app = FastAPI(title="Yerel AI Asistan")

class MessageRequest(BaseModel):
    text: str

class MessageResponse(BaseModel):
    response: str
    intent: str

@app.on_event("startup")
def startup():
    init_db(DB_PATH)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/message", response_model=MessageResponse)
async def handle_message(req: MessageRequest):
    conn = get_db(DB_PATH)
    try:
        today = date.today().isoformat()
        context = {
            "tasks": [dict(r) for r in conn.execute("SELECT id, title, priority, status, due_date FROM tasks WHERE status = 'bekliyor'").fetchall()],
            "habits": [dict(r) for r in conn.execute("SELECT id, name, target FROM habits WHERE active = 1").fetchall()],
            "events": [dict(r) for r in conn.execute("SELECT title, event_time FROM events WHERE DATE(event_time) >= ?", (today,)).fetchall()],
            "goals": [dict(r) for r in conn.execute("SELECT title, target_value, current_value, unit FROM goals WHERE status = 'aktif'").fetchall()],
        }
        history = [dict(r) for r in conn.execute("SELECT role, content FROM messages ORDER BY id DESC LIMIT 30").fetchall()]
        history.reverse()
        conn.execute("INSERT INTO messages (role, content) VALUES ('user', ?)", (req.text,))
        conn.commit()

        ai_result = await chat(req.text, history, context)
        intent = ai_result.get("intent", "general_chat")
        data = ai_result.get("data", {})
        ai_response = ai_result.get("response", "")

        handler_response = dispatch_intent(conn, intent, data)
        final_response = handler_response if handler_response else ai_response

        conn.execute("INSERT INTO messages (role, content) VALUES ('assistant', ?)", (final_response,))
        conn.commit()
        return MessageResponse(response=final_response, intent=intent)
    finally:
        conn.close()
