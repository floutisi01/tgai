import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, WebAppData
from aiogram.filters import CommandStart, Command

from config import BOT_TOKEN
from core.database import init_db, add_goal, get_user_goals, update_goal_progress, get_or_create_user_settings, get_last_progress_date
from core.ai_service import get_ai_response, generate_smart_reminder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await get_or_create_user_settings(message.from_user.id)
    await message.answer("Привет. Я твой личный дисциплинарный напарник.\n\nОсновной интерфейс — Mini App.\nЗдесь можно быстро спросить: /ask")
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
    MINI_APP_URL = "https://твой-проект.vercel.app"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Открыть Mini App", web_app=WebAppInfo(url=MINI_APP_URL))]])
    await message.answer("Главный экран:", reply_markup=kb)

@dp.message(Command("ask"))
async def cmd_ask(message: Message):
    q = message.text.replace("/ask", "").strip()
    if not q:
        await message.answer("Напиши вопрос после /ask")
        return
    goals = await get_user_goals(message.from_user.id, active_only=True)
    ctx = "Активные цели:\n" + "\n".join([f"- {g['title']}: {g['current_percent']}%" for g in goals[:3]])
    ans = await get_ai_response(q, ctx)
    await message.answer(ans)

@dp.message(F.web_app_data)
async def webapp_handler(message: Message):
    try:
        import json
        d = json.loads(message.web_app_data.data)
        if d.get("action") == "update_progress":
            await update_goal_progress(d["goal_id"], d["percent"], d.get("note", ""))
            await message.answer(f"Прогресс обновлён до {d['percent']}%")
        elif d.get("action") == "add_goal":
            gid = await add_goal(message.from_user.id, d["title"])
            await message.answer(f"Цель добавлена (ID: {gid})")
    except:
        await message.answer("Ошибка Mini App")

async def main():
    await init_db()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())