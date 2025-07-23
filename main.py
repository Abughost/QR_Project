import asyncio
import logging
import sys
from os import getenv

from aiogram import Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup
from dotenv import load_dotenv

from db.models import *
from db.config import *

load_dotenv()


TOKEN = getenv("BOT_TOKEN")


dp = Dispatcher()

dp.message(CommandStart(deep_link=True))
async def start_with_code(message: Message, command: CommandStart.Command):

    select_query =
    code = command.args

    if not code:
        await message.answer("QR kod yo'q!")
        return

    if code in used_codes:
        await message.answer("Bu QR code ishlatilgan ❌")
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

    with open("registrations.txt", "a") as file:
        file.write(f"{user_id},{name},{phone},{code}\n")

    used_codes.add(code)
    del pending_users[user_id]

    await message.answer("Muvaffaqiyatli konkurs ishtirokchisi bo'ldingiz! ✅", reply_markup=ReplyKeyboardRemove())



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
