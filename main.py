from aiohttp import web
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# Получаем токен из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен! Добавь в Environment Variables на Render.")

BOT_TOKEN = BOT_TOKEN.strip()
if "\n" in BOT_TOKEN or "\r" in BOT_TOKEN or " " in BOT_TOKEN:
    raise ValueError(f"BOT_TOKEN содержит недопустимые символы! Проверь токен: {repr(BOT_TOKEN)}")

print("Токен для проверки:", repr(BOT_TOKEN))
print("Длина токена:", len(BOT_TOKEN))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Главное меню выбора устройств
def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="iPhone 16", callback_data="cat_iphone16")],
        [InlineKeyboardButton(text="iPhone 16 Pro", callback_data="cat_iphone16pro")],
        [InlineKeyboardButton(text="iPhone 15 Pro Max", callback_data="cat_iphone15promax")],
        [InlineKeyboardButton(text="MacBook", callback_data="cat_macbook")],
        [InlineKeyboardButton(text="AirPods", callback_data="cat_airpods")],
        [InlineKeyboardButton(text="Обновить цены", callback_data="refresh")],
    ])

# Команда /start
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! Я — ApplePriceRU Bot\n"
        "Ищу самые выгодные цены на технику Apple по всем магазинам\n\n"
        "Выбери модель ↓",
        reply_markup=get_main_menu()
    )

# Обновление цен
@dp.callback_query(F.data == "refresh")
async def refresh(callback: CallbackQuery):
    await callback.answer("Цены обновляются каждые 15 минут автоматически", show_alert=True)

# Показ примера цен
@dp.callback_query(F.data.startswith("cat_"))
async def show_example(callback: CallbackQuery):
    model_dict = {
        "iphone16": "iPhone 16",
        "iphone16pro": "iPhone 16 Pro",
        "iphone15promax": "iPhone 15 Pro Max",
        "macbook": "MacBook Air",
        "airpods": "AirPods Pro"
    }
    model = model_dict.get(callback.data.split("_")[1], "Unknown")

    text = f"Самые низкие цены на {model} прямо сейчас:\n\n"
    text += "1. Restore — от 89 990 ₽\n   128 ГБ • Черный\n   https://restore.ru/catalog/iphone/iphone-16\n\n"
    text += "2. BigGeek — от 91 500 ₽\n   256 ГБ • Синий\n   https://biggeek.ru/catalog/iphone/iphone-16-pro\n\n"
    text += "3. re:Store — от 94 990 ₽\n   512 ГБ • Белый\n   https://re-store.ru/catalog/iphone/iphone-15-pro-max\n\n"
    text += "Нажми «Обновить цены», когда будут реальные данные!"

    kb = [
        [InlineKeyboardButton(text="Обновить цены", callback_data="refresh")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
    ]
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        disable_web_page_preview=True
    )

# Callback кнопки "Назад" для возвращения в главное меню
@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выбери модель ↓",
        reply_markup=get_main_menu()
    )

# Главная функция запуска бота с мини-сервером для Render
async def main():
    logging.info("Бот запущен и работает 24/7 на Render!")

    # Порт, который Render требует для Web Service
    PORT = int(os.environ.get("PORT", 10000))

    # Мини-сервер для Render, чтобы Render видел открытый порт
    async def handle(request):
        return web.Response(text="Bot is running!")

    app = web.Application()
    app.add_routes([web.get("/", handle)])  # маршрут "/" для проверки сервиса

    # Запускаем бота и мини-сервер параллельно
    await asyncio.gather(
        dp.start_polling(bot),        # твой бот
        web._run_app(app, port=PORT)  # мини-сервер для Render
    )

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
