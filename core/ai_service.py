import os
from openai import OpenAI
from dotenv import load_dotenv
from core.prompts import SYSTEM_PROMPT

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")

client = None

if GROK_API_KEY:
    client = OpenAI(
        api_key=GROK_API_KEY,
        base_url="https://api.x.ai/v1"
    )
else:
    print("⚠️ GROK_API_KEY / XAI_API_KEY не найден")

async def get_ai_response(user_message: str, context: str = "") -> str:
    if not client:
        return "Сейчас я на минималках. Добавь GROK_API_KEY."
    
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        
        if context:
            messages.append({"role": "user", "content": context})
        
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="grok-3-latest",           # или "grok-2-latest"
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Grok Error: {e}")
        return "Что-то пошло не так с Grok."

async def generate_smart_reminder(goal_title: str, current_percent: int, days_since: int) -> str:
    if not client:
        return f"Цель «{goal_title}» на {current_percent}%. Пора двигаться."
    
    prompt = f"""
    Цель пользователя: "{goal_title}"
    Текущий прогресс: {current_percent}%
    Дней без обновления: {days_since}
    
    Напиши короткое (1-2 предложения), честное напоминание с лёгким сарказмом.
    """
    try:
        response = client.chat.completions.create(
            model="grok-3-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except:
        return f"Цель «{goal_title}» на {current_percent}%. Пора двигаться."