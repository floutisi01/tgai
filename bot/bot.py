import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from config import BOT_TOKEN
from core.database import init_db, add_goal, get_user_goals, update_goal_progress, get_or_create_user_settings
from core.ai_service import get_ai_response, generate_smart_reminder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await get_or_create_user_settings(message.from_user.id)
    await message.answer("Привет. Я твой дисциплинарный напарник.\nОсновной интерфейс — Mini App.")

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
    MINI_APP_URL = "https://replit.com/@floutisi01flou/GitHub-Connect#no_universal_links"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть Mini App", web_app=WebAppInfo(url=MINI_APP_URL))]
    ])
    await message.answer("Главный экран:", reply_markup=kb)

@dp.message(Command("ask"))
async def cmd_ask(message: Message):
    q = message.text.replace("/ask", "").strip()
    if not q:
        return await message.answer("Напиши вопрос после /ask")
    
    goals = await get_user_goals(message.from_user.id, active_only=True)
    ctx = "Активные цели:\n" + "\n".join([f"- {g['title']}: {g['current_percent']}%" for g in goals[:3]])
    answer = await get_ai_response(q, ctx)
    await message.answer(answer)

@dp.message(F.web_app_data)
async def handle_webapp(message: Message):
    import json
    try:
        data = json.loads(message.web_app_data.data)
        if data.get("action") == "update_progress":
            await update_goal_progress(data["goal_id"], data["percent"])
            await message.answer(f"Прогресс обновлён до {data['percent']}%")
        elif data.get("action") == "add_goal":
            await add_goal(message.from_user.id, data["title"])
            await message.answer("Цель добавлена")
    except Exception as e:
        logger.error(e)
        await message.answer("Ошибка обработки Mini App")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())