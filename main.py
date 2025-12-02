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

# Модели iPhone и их реферальные ссылки
IPHONE_MODELS = {
    "iphone15": {
        "name": "iPhone 15",
        "memory_options": {
            "128GB": {
                "ЯндексМаркет": "https://yandex.ru/market/iphone15_128gb",
                "Ozon": "https://ozon.ru/iphone15_128gb"
            },
            "256GB": {
                "ЯндексМаркет": "https://yandex.ru/market/iphone15_256gb",
                "Ozon": "https://ozon.ru/iphone15_256gb"
            }
        },
        "colors": ["Черный", "Белый", "Синий"]
    },
    "iphone15pro": {
        "name": "iPhone 15 Pro",
        "memory_options": {
            "128GB": {
                "ЯндексМаркет": "https://yandex.ru/market/iphone15pro_128gb",
                "Ozon": "https://ozon.ru/iphone15pro_128gb"
            },
            "256GB": {
                "ЯндексМаркет": "https://yandex.ru/market/iphone15pro_256gb",
                "Ozon": "https://ozon.ru/iphone15pro_256gb"
            }
        },
        "colors": ["Черный", "Белый", "Золотой"]
    },
    "iphone15promax": {
        "name": "iPhone 15 Pro Max",
        "memory_options": {
            "256GB": {
                "ЯндексМаркет": "https://yandex.ru/market/iphone15promax_256gb",
                "Ozon": "https://ozon.ru/iphone15promax_256gb"
            },
            "512GB": {
                "ЯндексМаркет": "https://yandex.ru/market/iphone15promax_512gb",
                "Ozon": "https://ozon.ru/iphone15promax_512gb"
            }
        },
        "colors": ["Серый", "Белый", "Синий"]
    }
}

# Главное меню моделей iPhone
def get_iphone_menu():
    keyboard = []
    for code, info in IPHONE_MODELS.items():
        keyboard.append([InlineKeyboardButton(text=info["name"], callback_data=f"model_{code}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Меню памяти для выбранной модели
def get_memory_menu(model_code):
    keyboard = []
    memories = IPHONE_MODELS[model_code]["memory_options"].keys()
    for mem in memories:
        keyboard.append([InlineKeyboardButton(text=mem, callback_data=f"memory_{model_code}_{mem}")])
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_models")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Команда /start
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! Выбери модель iPhone ↓",
        reply_markup=get_iphone_menu()
    )

# Выбор модели
@dp.callback_query(F.data.startswith("model_"))
async def select_model(callback: CallbackQuery):
    model_code = callback.data.split("_")[1]
    await callback.message.edit_text(
        f"Вы выбрали {IPHONE_MODELS[model_code]['name']}. Выберите память:",
        reply_markup=get_memory_menu(model_code)
    )

# Назад к выбору моделей
@dp.callback_query(F.data == "back_to_models")
async def back_to_models(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите модель iPhone ↓",
        reply_markup=get_iphone_menu()
    )

# Выбор памяти и показ ссылок
@dp.callback_query(F.data.startswith("memory_"))
async def select_memory(callback: CallbackQuery):
    _, model_code, mem = callback.data.split("_")
    model_info = IPHONE_MODELS[model_code]
    memory_info = model_info["memory_options"][mem]

    text = f"Ссылки на {model_info['name']} {mem}:\n\n"
    for shop, link in memory_info.items():
        text += f"{shop}: {link}\n"
    text += "\n⬅️ Назад для выбора другой модели или памяти."

    keyboard = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"model_{model_code}")]
    ]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

# Мини-сервер для Render
async def main():
    logging.info("Бот запущен и работает 24/7 на Render!")

    PORT = int(os.environ.get("PORT", 10000))

    async def handle(request):
        return web.Response(text="Bot is running!")

    app = web.Application()
    app.add_routes([web.get("/", handle)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Web server запущен на порту {PORT}")

    # Запуск бота
    await dp.start_polling(bot)

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
