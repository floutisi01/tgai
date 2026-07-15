import google.generativeai as genai
import os
from dotenv import load_dotenv
from core.prompts import SYSTEM_PROMPT

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = None

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
else:
    print("⚠️ GEMINI_API_KEY не найден")

async def get_ai_response(user_message: str, context: str = "") -> str:
    if not model:
        return "Сейчас я на минималках. Добавь GEMINI_API_KEY в .env"
    
    try:
        full_prompt = f"{context}\n\nПользователь: {user_message}"
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Что-то пошло не так с ИИ."

async def generate_smart_reminder(goal_title: str, current_percent: int, days_since: int) -> str:
    if not model:
        return f"Цель «{goal_title}» на {current_percent}%. Пора двигаться."
    
    prompt = f"""
    Цель пользователя: "{goal_title}"
    Текущий прогресс: {current_percent}%
    Дней без обновления: {days_since}
    
    Напиши короткое (1-2 предложения), честное напоминание с лёгким сарказмом.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return f"Цель «{goal_title}» на {current_percent}%. Пора двигаться."