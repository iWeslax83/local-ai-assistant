import sqlite3
from core.intents.tasks import handle_add_task, handle_list_tasks, handle_complete_task
from core.intents.events import handle_add_event, handle_list_events
from core.intents.notes import handle_add_note, handle_search_notes
from core.intents.reminders import handle_add_reminder
from core.intents.habits import handle_add_habit, handle_log_habit, handle_habit_status
from core.intents.expenses import handle_add_expense, handle_expense_summary
from core.intents.moods import handle_log_mood, handle_mood_trend
from core.intents.goals import handle_add_goal, handle_update_goal, handle_goal_status
from core.intents.preferences import handle_update_preference
from core.intents.self_modify import handle_modify_code, handle_confirm_code_change, handle_rollback_code

INTENT_HANDLERS = {
    "add_task": handle_add_task,
    "list_tasks": handle_list_tasks,
    "complete_task": handle_complete_task,
    "add_event": handle_add_event,
    "list_events": handle_list_events,
    "add_note": handle_add_note,
    "search_notes": handle_search_notes,
    "add_reminder": handle_add_reminder,
    "add_habit": handle_add_habit,
    "log_habit": handle_log_habit,
    "habit_status": handle_habit_status,
    "add_expense": handle_add_expense,
    "expense_summary": handle_expense_summary,
    "log_mood": handle_log_mood,
    "mood_trend": handle_mood_trend,
    "add_goal": handle_add_goal,
    "update_goal": handle_update_goal,
    "goal_status": handle_goal_status,
    "update_preference": handle_update_preference,
    "modify_code": handle_modify_code,
    "confirm_code_change": handle_confirm_code_change,
    "rollback_code": handle_rollback_code,
}

def dispatch_intent(conn: sqlite3.Connection, intent: str, data: dict) -> str | None:
    handler = INTENT_HANDLERS.get(intent)
    if handler:
        return handler(conn, data)
    return None
