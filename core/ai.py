import json
import re
import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1:8b"

INTENT_LIST = """
Desteklenen intent'ler:
- add_task: Görev ekle (data: title, priority, due_date)
- list_tasks: Görevleri listele (data: {})
- complete_task: Görevi tamamla (data: title)
- add_event: Etkinlik ekle (data: title, event_time, remind_at)
- list_events: Etkinlikleri listele (data: {})
- add_note: Not kaydet (data: content, tag)
- search_notes: Not ara (data: query)
- add_reminder: Hatırlatma kur (data: message, remind_at)
- add_habit: Alışkanlık tanımla (data: name, target)
- log_habit: Alışkanlık kaydet (data: name, value)
- habit_status: Alışkanlık durumu (data: {})
- add_expense: Harcama kaydet (data: amount, category, description)
- expense_summary: Harcama özeti (data: period)
- log_mood: Ruh hali kaydet (data: level, journal)
- mood_trend: Ruh hali trendi (data: period)
- add_goal: Hedef ekle (data: title, target_value, unit, deadline)
- update_goal: Hedef güncelle (data: title, value)
- goal_status: Hedef durumu (data: {})
- update_preference: Ayar değiştir (data: key, value)
- modify_code: Kod değiştir (data: request)
- confirm_code_change: Kod değişikliğini onayla (data: {})
- rollback_code: Son değişikliği geri al (data: {})
- general_chat: Serbest sohbet (data: {})
"""


def build_system_prompt(context: dict) -> str:
    tasks_str = ""
    if context.get("tasks"):
        tasks_str = "Bugünkü görevler:\n"
        for t in context["tasks"]:
            tasks_str += f"- [{t['status']}] {t['title']} (öncelik: {t.get('priority', 'normal')})\n"

    habits_str = ""
    if context.get("habits"):
        habits_str = "Aktif alışkanlıklar:\n"
        for h in context["habits"]:
            habits_str += f"- {h['name']} (hedef: {h['target']})\n"

    events_str = ""
    if context.get("events"):
        events_str = "Bugünkü etkinlikler:\n"
        for e in context["events"]:
            events_str += f"- {e['title']} ({e['event_time']})\n"

    goals_str = ""
    if context.get("goals"):
        goals_str = "Aktif hedefler:\n"
        for g in context["goals"]:
            goals_str += f"- {g['title']}: {g['current_value']}/{g['target_value']} {g['unit']}\n"

    return f"""Sen Türkçe konuşan kişisel bir üretkenlik asistanısın. Kullanıcıyla WhatsApp üzerinden iletişim kuruyorsun.

Kurallar:
- Her zaman Türkçe yanıt ver
- Samimi ve yardımsever ol
- Tarih formatı: GG.AA.YYYY
- Saat formatı: 24 saat (ör: 14:30)
- "bugün", "yarın", "dün" gibi göreceli tarihleri anla

{INTENT_LIST}

Yanıtını her zaman şu JSON formatında ver:
{{"intent": "<intent_adı>", "data": {{<ilgili_veriler>}}, "response": "<kullanıcıya_gösterilecek_mesaj>"}}

Güncel durum:
{tasks_str}
{habits_str}
{events_str}
{goals_str}
"""


def parse_ai_response(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{[^{}]*"intent"[^{}]*\}', raw)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    match = re.search(r'\{.*"intent".*\}', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"intent": "general_chat", "data": {}, "response": raw}


async def chat(
    user_message: str,
    message_history: list[dict],
    context: dict,
) -> dict:
    system_prompt = build_system_prompt(context)

    messages = [{"role": "system", "content": system_prompt}]
    for msg in message_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.3},
            },
        )
        response.raise_for_status()
        data = response.json()

    raw_content = data["message"]["content"]
    return parse_ai_response(raw_content)
