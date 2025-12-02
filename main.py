import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
print(repr(BOT_TOKEN))

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен! Добавь в Environment Variables на Render.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="iPhone 16", callback_data="cat_iphone16")],
        [InlineKeyboardButton(text="iPhone 16 Pro", callback_data="cat_iphone16pro")],
        [InlineKeyboardButton(text="iPhone 15 Pro Max", callback_data="cat_iphone15promax")],
        [InlineKeyboardButton(text="MacBook", callback_data="cat_macbook")],
        [InlineKeyboardButton(text="AirPods", callback_data="cat_airpods")],
        [InlineKeyboardButton(text="Обновить цены", callback_data="refresh")],
    ])
    await message.answer(
        "Привет! Я — ApplePriceRU Bot\n"
        "Ищу самые выгодные цены на технику Apple по всем магазинам\n\n"
        "Выбери модель ↓",
        reply_markup=kb
    )

@dp.callback_query(F.data == "refresh")
async def refresh(callback: CallbackQuery):
    await callback.answer("Цены обновляются каждые 15 минут автоматически", show_alert=True)

@dp.callback_query(F.data.startswith("cat_"))
async def show_example(callback: CallbackQuery):
    model = {
        "iphone16": "iPhone 16",
        "iphone16pro": "iPhone 16 Pro",
        "iphone15promax": "iPhone 15 Pro Max",
        "macbook": "MacBook Air",
        "airpods": "AirPods Pro"
    }[callback.data.split("_")[1]]

    text = f"Самые низкие цены на {model} прямо сейчас:\n\n"
    text += "1. Restore — от 89 990 ₽\n   128 ГБ • Черный\n   https://restore.ru/catalog/iphone/iphone-16\n\n"
    text += "2. BigGeek — от 91 500 ₽\n   256 ГБ • Синий\n   https://biggeek.ru/catalog/iphone/iphone-16-pro\n\n"
    text += "3. re:Store — от 94 990 ₽\n   512 ГБ • Белый\n   https://re-store.ru/catalog/iphone/iphone-15-pro-max\n\n"
    text += "Нажми «Обновить цены», когда будут реальные данные!"

    kb = [[InlineKeyboardButton(text="Обновить цены", callback_data="refresh")]]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), disable_web_page_preview=True)

async def main():
    logging.info("Бот запущен и работает 24/7 на Render!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
