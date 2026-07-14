import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict

DB_PATH = "bot_data.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('CREATE TABLE IF NOT EXISTS goals (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, title TEXT NOT NULL, description TEXT, target_percent INTEGER DEFAULT 100, current_percent INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, deadline DATE, is_active BOOLEAN DEFAULT 1)')
        await db.execute('CREATE TABLE IF NOT EXISTS progress_history (id INTEGER PRIMARY KEY AUTOINCREMENT, goal_id INTEGER NOT NULL, percent INTEGER NOT NULL, note TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        await db.execute('CREATE TABLE IF NOT EXISTS user_settings (user_id INTEGER PRIMARY KEY, reminder_enabled BOOLEAN DEFAULT 1, reminder_time TEXT DEFAULT \'09:00\', timezone TEXT DEFAULT \'Europe/Moscow\')')
        await db.commit()

async def add_goal(user_id: int, title: str, description: str = "", target: int = 100):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT INTO goals (user_id, title, description, target_percent) VALUES (?, ?, ?, ?)', (user_id, title, description, target))
        await db.commit()
        return db.lastrowid

async def get_user_goals(user_id: int, active_only: bool = True):
    async with aiosqlite.connect(DB_PATH) as db:
        q = 'SELECT * FROM goals WHERE user_id = ?' + (' AND is_active = 1' if active_only else '') + ' ORDER BY created_at DESC'
        cursor = await db.execute(q, (user_id,))
        rows = await cursor.fetchall()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]

async def update_goal_progress(goal_id: int, new_percent: int, note: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE goals SET current_percent = ? WHERE id = ?', (new_percent, goal_id))
        await db.execute('INSERT INTO progress_history (goal_id, percent, note) VALUES (?, ?, ?)', (goal_id, new_percent, note))
        await db.commit()

async def get_or_create_user_settings(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        if row: return dict(zip([col[0] for col in cursor.description], row))
        await db.execute('INSERT INTO user_settings (user_id) VALUES (?)', (user_id,))
        await db.commit()
        return {"user_id": user_id, "reminder_enabled": True, "reminder_time": "09:00"}

async def update_reminder_settings(user_id: int, reminder_time: str = None, enabled: bool = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if reminder_time: await db.execute('UPDATE user_settings SET reminder_time = ? WHERE user_id = ?', (reminder_time, user_id))
        if enabled is not None: await db.execute('UPDATE user_settings SET reminder_enabled = ? WHERE user_id = ?', (enabled, user_id))
        await db.commit()

async def get_last_progress_date(goal_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT created_at FROM progress_history WHERE goal_id = ? ORDER BY created_at DESC LIMIT 1', (goal_id,))
        row = await cursor.fetchone()
        return row[0] if row else None
