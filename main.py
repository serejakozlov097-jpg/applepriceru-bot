from aiohttp import web
import asyncio
import logging
import os
import random
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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Модели iPhone и их реферальные ссылки
IPHONE_MODELS = {
    "iphone15": {
        "name": "iPhone 15",
        "memory_options": {
            "128GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "256GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "512GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "1TB": {"ЯндексМаркет": "...", "Ozon": "..."},
        },
        "colors": ["Черный", "Белый", "Синий"]
    },
    "iphone15plus": {
        "name": "iPhone 15 Plus",
        "memory_options": {
            "128GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "256GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "512GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "1TB": {"ЯндексМаркет": "...", "Ozon": "..."},
        },
        "colors": ["Черный", "Белый", "Красный"]
    },
    "iphone15pro": {
        "name": "iPhone 15 Pro",
        "memory_options": {
            "128GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "256GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "512GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "1TB": {"ЯндексМаркет": "...", "Ozon": "..."},
        },
        "colors": ["Черный", "Белый", "Золотой"]
    },
    "iphone15promax": {
        "name": "iPhone 15 Pro Max",
        "memory_options": {
            "128GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "256GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "512GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "1TB": {"ЯндексМаркет": "...", "Ozon": "..."},
        },
        "colors": ["Серый", "Белый", "Синий"]
    },

    # Дальше твои остальные модели (16, 16 Plus и т.д.)
    "iphone16": {
        "name": "iPhone 16",
        "memory_options": {
            "128GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "256GB": {"ЯндексМаркет": "...", "Ozon": "..."},
        },
        "colors": ["Черный", "Белый", "Синий"]
    },
    "iphone16plus": {
        "name": "iPhone 16 Plus",
        "memory_options": {
            "128GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "256GB": {"ЯндексМаркет": "...", "Ozon": "..."},
        },
        "colors": ["Черный", "Белый", "Красный"]
    },
    "iphone16pro": {
        "name": "iPhone 16 Pro",
        "memory_options": {
            "128GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "256GB": {"ЯндексМаркет": "...", "Ozon": "..."},
        },
        "colors": ["Черный", "Белый", "Золотой"]
    },
    "iphone16promax": {
        "name": "iPhone 16 Pro Max",
        "memory_options": {
            "256GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "512GB": {"ЯндексМаркет": "...", "Ozon": "..."},
        },
        "colors": ["Серый", "Белый", "Синий"]
    },
    "iphone17": {
        "name": "iPhone 17",
        "memory_options": {
            "128GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "256GB": {"ЯндексМаркет": "...", "Ozon": "..."},
        },
        "colors": ["Черный", "Белый", "Красный"]
    },
    "iphone17air": {
        "name": "iPhone 17 Air",
        "memory_options": {
            "128GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "256GB": {"ЯндексМаркет": "...", "Ozon": "..."},
        },
        "colors": ["Серый", "Белый", "Синий"]
    },
    "iphone17pro": {
        "name": "iPhone 17 Pro",
        "memory_options": {
            "256GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "512GB": {"ЯндексМаркет": "...", "Ozon": "..."},
        },
        "colors": ["Черный", "Белый", "Золотой"]
    },
    "iphone17promax": {
        "name": "iPhone 17 Pro Max",
        "memory_options": {
            "512GB": {"ЯндексМаркет": "...", "Ozon": "..."},
            "1TB": {"ЯндексМаркет": "...", "Ozon": "..."},
        },
        "colors": ["Серый", "Белый", "Золотой"]
    },
}

# Главное меню моделей iPhone (с уникальным суффиксом)
def get_iphone_menu():
    keyboard = []
    suffix = str(random.randint(1, 999999))

    for code, info in IPHONE_MODELS.items():
        keyboard.append([
            InlineKeyboardButton(
                text=info["name"],
                callback_data=f"model_{code}_{suffix}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Меню памяти
def get_memory_menu(model_code):
    keyboard = []
    memories = IPHONE_MODELS[model_code]["memory_options"].keys()

    for mem in memories:
        keyboard.append([
            InlineKeyboardButton(
                text=mem,
                callback_data=f"memory_{model_code}_{mem}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_models")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Команда /start
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Выбери модель iPhone ↓", reply_markup=get_iphone_menu())

# Выбор модели
@dp.callback_query(F.data.startswith("model_"))
async def select_model(callback: CallbackQuery):
    parts = callback.data.split("_")
    model_code = parts[1]

    await callback.message.edit_text(
        f"Вы выбрали {IPHONE_MODELS[model_code]['name']}. Выберите память:",
        reply_markup=get_memory_menu(model_code)
    )

# Назад
@dp.callback_query(F.data == "back_to_models")
async def back_to_models(callback: CallbackQuery):
    await callback.message.edit_text("Выберите модель iPhone ↓", reply_markup=get_iphone_menu())

# Выбор памяти
@dp.callback_query(F.data.startswith("memory_"))
async def select_memory(callback: CallbackQuery):
    _, model_code, mem = callback.data.split("_")
    model_info = IPHONE_MODELS[model_code]
    memory_info = model_info["memory_options"][mem]

    text = f"Ссылки на {model_info['name']} {mem}:\n\n"

    for shop, link in memory_info.items():
        color = random.choice(model_info["colors"])
        text += f"{shop} ({color}): {link}\n"

    keyboard = [[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_models")]]

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

# Мини-сервер для Render
async def main():
    logging.info("Бот запущен!")

    PORT = int(os.environ.get("PORT", 10000))

    async def handle(request):
        return web.Response(text="Bot is running!")

    app = web.Application()
    app.add_routes([web.get("/", handle)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
