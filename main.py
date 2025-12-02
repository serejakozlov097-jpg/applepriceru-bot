from aiohttp import web
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# ------------------- Настройка бота -------------------
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

# ------------------- Данные о моделях -------------------
# Для каждой модели — доступные цвета и память с реферальными ссылками
IPHONE_MODELS = {
    "iphone15": {
        "name": "iPhone 15",
        "variants": {
            "128GB": {
                "Черный": {"yandex": "https://yandex.ru/iphone15-128-black", "ozon": "https://ozon.ru/iphone15-128-black"},
                "Синий": {"yandex": "https://yandex.ru/iphone15-128-blue", "ozon": "https://ozon.ru/iphone15-128-blue"}
            },
            "256GB": {
                "Черный": {"yandex": "https://yandex.ru/iphone15-256-black", "ozon": "https://ozon.ru/iphone15-256-black"},
                "Синий": {"yandex": "https://yandex.ru/iphone15-256-blue", "ozon": "https://ozon.ru/iphone15-256-blue"}
            }
        }
    },
    "iphone15pro": {
        "name": "iPhone 15 Pro",
        "variants": {
            "128GB": {
                "Серебристый": {"yandex": "https://yandex.ru/iphone15pro-128-silver", "ozon": "https://ozon.ru/iphone15pro-128-silver"},
                "Золотой": {"yandex": "https://yandex.ru/iphone15pro-128-gold", "ozon": "https://ozon.ru/iphone15pro-128-gold"}
            }
        }
    },
    "iphone16": {
        "name": "iPhone 16",
        "variants": {
            "256GB": {
                "Черный": {"yandex": "https://yandex.ru/iphone16-256-black", "ozon": "https://ozon.ru/iphone16-256-black"},
                "Белый": {"yandex": "https://yandex.ru/iphone16-256-white", "ozon": "https://ozon.ru/iphone16-256-white"}
            }
        }
    }
    # Добавляй остальные модели по аналогии
}

# ------------------- Функции генерации клавиатур -------------------
def get_model_menu():
    kb = []
    for code, model in IPHONE_MODELS.items():
        kb.append([InlineKeyboardButton(text=model["name"], callback_data=f"model_{code}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_memory_menu(model_code):
    kb = []
    model = IPHONE_MODELS[model_code]
    for memory in model["variants"].keys():
        kb.append([InlineKeyboardButton(text=memory, callback_data=f"memory_{model_code}_{memory}")])
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_models")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_color_menu(model_code, memory):
    kb = []
    model = IPHONE_MODELS[model_code]
    for color in model["variants"][memory]:
        kb.append([InlineKeyboardButton(text=color, callback_data=f"color_{model_code}_{memory}_{color}")])
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_memory_{model_code}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_shop_menu(model_code, memory, color):
    kb = []
    variant = IPHONE_MODELS[model_code]["variants"][memory][color]
    for shop_name, link in variant.items():
        kb.append([InlineKeyboardButton(text=shop_name, url=link)])
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_colors_{model_code}_{memory}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ------------------- Обработчики -------------------
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Выбери модель iPhone:", reply_markup=get_model_menu())

@dp.callback_query(F.data.startswith("model_"))
async def select_model(callback: CallbackQuery):
    model_code = callback.data.split("_")[1]
    await callback.message.edit_text("Выбери память:", reply_markup=get_memory_menu(model_code))

@dp.callback_query(F.data.startswith("memory_"))
async def select_memory(callback: CallbackQuery):
    _, model_code, memory = callback.data.split("_")
    await callback.message.edit_text("Выбери цвет:", reply_markup=get_color_menu(model_code, memory))

@dp.callback_query(F.data.startswith("color_"))
async def select_color(callback: CallbackQuery):
    _, model_code, memory, color = callback.data.split("_")
    await callback.message.edit_text("Выбери магазин:", reply_markup=get_shop_menu(model_code, memory, color))

# Назад на уровень моделей
@dp.callback_query(F.data == "back_to_models")
async def back_to_models(callback: CallbackQuery):
    await callback.message.edit_text("Выбери модель iPhone:", reply_markup=get_model_menu())

# Назад на уровень памяти
@dp.callback_query(F.data.startswith("back_to_memory_"))
async def back_to_memory(callback: CallbackQuery):
    model_code = callback.data.split("_")[3]
    await callback.message.edit_text("Выбери память:", reply_markup=get_memory_menu(model_code))

# Назад на уровень цветов
@dp.callback_query(F.data.startswith("back_to_colors_"))
async def back_to_colors(callback: CallbackQuery):
    _, _, model_code, memory = callback.data.split("_")
    await callback.message.edit_text("Выбери цвет:", reply_markup=get_color_menu(model_code, memory))

# ------------------- Главная функция -------------------
async def main():
    logging.info("Бот запущен и работает 24/7 на Render!")
    PORT = int(os.environ.get("PORT", 10000))

    async def handle(request):
        return web.Response(text="Bot is running!")

    app = web.Application()
    app.add_routes([web.get("/", handle)])

    # Запускаем бот и веб-сервер параллельно
    await asyncio.gather(
        dp.start_polling(bot),
        web.run_app(app, port=PORT)
    )

if __name__ == "__main__":
    asyncio.run(main())
