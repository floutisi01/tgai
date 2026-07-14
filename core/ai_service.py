import google.generativeai as genai
import os
from dotenv import load_dotenv
from core.prompts import SYSTEM_PROMPT

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)

async def get_ai_response(user_message: str, context: str = "") -> str:
    if not model: return "Сейчас я на минималках. Добавь GEMINI_API_KEY."
    try:
        response = model.generate_content(f"{context}\n\nПользователь: {user_message}")
        return response.text.strip()
    except:
        return "Ошибка с ИИ."

async def generate_smart_reminder(goal_title: str, current_percent: int, days_since: int) -> str:
    if not model:
        return f"Цель «{goal_title}» на {current_percent}%. Пора двигаться."
    context = f"Цель: {goal_title} | Прогресс: {current_percent}% | Дней без обновлений: {days_since}\nКороткое напоминание с сарказмом."
    try:
        return model.generate_content(context).text.strip()
    except:
        return f"Цель «{goal_title}» на {current_percent}%. Пора двигаться."
