import os
from openai import OpenAI
from dotenv import load_dotenv
from core.prompts import SYSTEM_PROMPT

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")

if not GROK_API_KEY:
    print("⚠️ GROK_API_KEY не найден в переменных Replit")
    client = None
else:
    client = OpenAI(
        api_key=GROK_API_KEY,
        base_url="https://api.x.ai/v1"
    )

async def get_ai_response(user_message: str, context: str = "") -> str:
    if not client:
        return "GROK_API_KEY не найден. Добавь его в Secrets Replit."
    
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if context:
            messages.append({"role": "user", "content": context})
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="grok-2-1212",           # ← более стабильная модель
            messages=messages,
            temperature=0.7,
            max_tokens=700
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Grok API Error: {e}")   # ← это важно, смотри логи
        return "Что-то пошло не так с ИИ."

async def generate_smart_reminder(goal_title: str, current_percent: int, days_since: int) -> str:
    if not client:
        return f"Цель «{goal_title}» на {current_percent}%. Пора двигаться."
    
    prompt = f'Цель: "{goal_title}". Прогресс: {current_percent}%. Напиши короткое напоминание с сарказмом.'
    
    try:
        response = client.chat.completions.create(
            model="grok-2-1212",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Grok Reminder Error: {e}")
        return f"Цель «{goal_title}» на {current_percent}%. Пора двигаться."