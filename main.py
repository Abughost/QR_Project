import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import psycopg2

from db.models import *

pending_users = {}
used_codes = set()

load_dotenv()

TOKEN = getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env file")

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            host=getenv("DB_HOST"),
            port=getenv("DB_PORT")
        )
        conn.autocommit = True
        return conn
    except psycopg2.Error as e:
        print(f"Database ulanish xatosi: {e}")
        return None

def load_initial_data():
    global pending_users, used_codes
    with get_db_connection() as conn:
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code FROM qr_codes WHERE used = true")
            used_codes = set(row[0] for row in cursor.fetchall())
            pending_users = {}  # Yangi foydalanuvchilar uchun bo'sh

load_initial_data()

@dp.message(CommandStart(deep_link=True))
async def start_with_code(message: Message, command: CommandStart):
    select_query = "SELECT code, user_id FROM qr_codes WHERE used = false"
    code = command.args

    if not code:
        await message.answer("QR kod yo'q!")
        return

    with get_db_connection() as conn:
        if conn:
            cursor = conn.cursor()
            cursor.execute(select_query)
            available_codes = {row[0] for row in cursor.fetchall()}
            if code in used_codes or code not in available_codes:
                await message.answer("Bu QR code ishlatilgan yoki mavjud emas ❌")
                return

    user_id = message.from_user.id
    pending_users[user_id] = {"code": code}
    await message.answer("Full ismingizni kiriting 👇")

@dp.message(F.text)
async def handle_name(message: Message):
    user_id = message.from_user.id

    if user_id not in pending_users or "name" in pending_users[user_id]:
        return

    pending_users[user_id]["name"] = message.text

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Kontakt ulashish 📱", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Telefon raqamingizni ulashing 👇", reply_markup=kb)

@dp.message(F.contact)
async def handle_contact(message: Message):
    user_id = message.from_user.id

    if user_id not in pending_users or "name" not in pending_users[user_id]:
        return

    name = pending_users[user_id]["name"]
    phone = message.contact.phone_number
    code = pending_users[user_id]["code"]

    with get_db_connection() as conn:
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE qr_codes SET used = true, user_id = %s WHERE code = %s", (user_id, code))
            conn.commit()

    used_codes.add(code)
    del pending_users[user_id]

    await message.answer("Muvaffaqiyatli konkurs ishtirokchisi bo'ldingiz! ✅", reply_markup=ReplyKeyboardRemove())

async def main():
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        logging.info("Bot ishga tushdi!")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Bot xatosi: {e}")

if __name__ == "__main__":
    asyncio.run(main())