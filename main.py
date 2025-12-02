from aiohttp import web
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# ===== Настройка токена =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен! Добавь в Environment Variables на Render.")
BOT_TOKEN = BOT_TOKEN.strip()
if "\n" in BOT_TOKEN or "\r" in BOT_TOKEN or " " in BOT_TOKEN:
    raise ValueError(f"BOT_TOKEN содержит недопустимые символы! Проверь токен: {repr(BOT_TOKEN)}")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ===== Данные о моделях iPhone =====
IPHONES = {
    "iPhone 15": {
        "128GB": {
            "Черный": {"Яндекс.Маркет": "https://yandex.market/iphone15_128_black", "Ozon": "https://ozon.ru/iphone15_128_black"},
            "Белый": {"Яндекс.Маркет": "https://yandex.market/iphone15_128_white", "Ozon": "https://ozon.ru/iphone15_128_white"},
        },
        "256GB": {
            "Черный": {"Яндекс.Маркет": "https://yandex.market/iphone15_256_black", "Ozon": "https://ozon.ru/iphone15_256_black"},
            "Белый": {"Яндекс.Маркет": "https://yandex.market/iphone15_256_white", "Ozon": "https://ozon.ru/iphone15_256_white"},
        }
    },
    "iPhone 15 Pro": {
        "128GB": {
            "Серый": {"Яндекс.Маркет": "https://yandex.market/iphone15pro_128_gray", "Ozon": "https://ozon.ru/iphone15pro_128_gray"},
            "Синий": {"Яндекс.Маркет": "https://yandex.market/iphone15pro_128_blue", "Ozon": "https://ozon.ru/iphone15pro_128_blue"},
        }
    },
    "iPhone 15 Pro Max": {
        "256GB": {
            "Черный": {"Яндекс.Маркет": "https://yandex.market/iphone15promax_256_black", "Ozon": "https://ozon.ru/iphone15promax_256_black"},
        }
    },
    "iPhone 16": {
        "128GB": {
            "Черный": {"Яндекс.Маркет": "https://yandex.market/iphone16_128_black", "Ozon": "https://ozon.ru/iphone16_128_black"},
            "Белый": {"Яндекс.Маркет": "https://yandex.market/iphone16_128_white", "Ozon": "https://ozon.ru/iphone16_128_white"},
        },
        "256GB": {
            "Черный": {"Яндекс.Маркет": "https://yandex.market/iphone16_256_black", "Ozon": "https://ozon.ru/iphone16_256_black"},
        }
    },
    "iPhone 16 Pro": {
        "128GB": {
            "Серый": {"Яндекс.Маркет": "https://yandex.market/iphone16pro_128_gray", "Ozon": "https://ozon.ru/iphone16pro_128_gray"},
        }
    },
    "iPhone 16 Pro Max": {
        "256GB": {
            "Синий": {"Яндекс.Маркет": "https://yandex.market/iphone16promax_256_blue", "Ozon": "https://ozon.ru/iphone16promax_256_blue"},
        }
    },
    "iPhone 17": {
        "128GB": {
            "Красный": {"Яндекс.Маркет": "https://yandex.market/iphone17_128_red", "Ozon": "https://ozon.ru/iphone17_128_red"},
            "Черный": {"Яндекс.Маркет": "https://yandex.market/iphone17_128_black", "Ozon": "https://ozon.ru/iphone17_128_black"},
        }
    },
    "iPhone 17 Air": {
        "256GB": {
            "Серебристый": {"Яндекс.Маркет": "https://yandex.market/iphone17air_256_silver", "Ozon": "https://ozon.ru/iphone17air_256_silver"},
        }
    },
    "iPhone 17 Pro": {
        "512GB": {
            "Синий": {"Яндекс.Маркет": "https://yandex.market/iphone17pro_512_blue", "Ozon": "https://ozon.ru/iphone17pro_512_blue"},
        }
    },
    "iPhone 17 Pro Max": {
        "1TB": {
            "Черный": {"Яндекс.Маркет": "https://yandex.market/iphone17promax_1tb_black", "Ozon": "https://ozon.ru/iphone17promax_1tb_black"},
        }
    }
}

# ===== Функции меню =====
def get_model_menu():
    buttons = [[InlineKeyboardButton(text=model, callback_data=f"model_{model}")] for model in IPHONES.keys()]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_memory_menu(model):
    memories = IPHONES[model].keys()
    buttons = [[InlineKeyboardButton(text=mem, callback_data=f"memory_{model}_{mem}")] for mem in memories]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_models")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_color_menu(model, memory):
    colors = IPHONES[model][memory].keys()
    buttons = [[InlineKeyboardButton(text=color, callback_data=f"color_{model}_{memory}_{color}")] for color in colors]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_memory_{model}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_market_menu(model, memory, color):
    marketplaces = IPHONES[model][memory][color]
    buttons = [[InlineKeyboardButton(text=market, url=url)] for market, url in marketplaces.items()]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_colors_{model}_{memory}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ===== Обработчики =====
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Выберите модель iPhone:", reply_markup=get_model_menu())

@dp.callback_query(F.data.startswith("model_"))
async def model_handler(callback: CallbackQuery):
    model = callback.data.split("_", 1)[1]
    await callback.message.edit_text(f"Выберите объём памяти для {model}:", reply_markup=get_memory_menu(model))

@dp.callback_query(F.data.startswith("memory_"))
async def memory_handler(callback: CallbackQuery):
    _, model, memory = callback.data.split("_", 2)
    await callback.message.edit_text(f"Выберите цвет для {model} ({memory}):", reply_markup=get_color_menu(model, memory))

@dp.callback_query(F.data.startswith("color_"))
async def color_handler(callback: CallbackQuery):
    _, model, memory, color = callback.data.split("_", 3)
    await callback.message.edit_text(f"Выберите маркетплейс для {model} {memory} {color}:", reply_markup=get_market_menu(model, memory, color))

# ===== Кнопки "Назад" =====
@dp.callback_query(F.data == "back_to_models")
async def back_to_models(callback: CallbackQuery):
    await callback.message.edit_text("Выберите модель iPhone:", reply_markup=get_model_menu())

@dp.callback_query(F.data.startswith("back_to_memory_"))
async def back_to_memory(callback: CallbackQuery):
    model = callback.data.replace("back_to_memory_", "")
    await callback.message.edit_text(f"Выберите объём памяти для {model}:", reply_markup=get_memory_menu(model))

@dp.callback_query(F.data.startswith("back_to_colors_"))
async def back_to_colors(callback: CallbackQuery):
    _, model, memory = callback.data.split("_", 2)
    await callback.message.edit_text(f"Выберите цвет для {model} ({memory}):", reply_markup=get_color_menu(model, memory))

# ===== Мини-сервер для Render =====
async def main():
    logging.info("Бот запущен и работает 24/7 на Render!")
    PORT = int(os.environ.get("PORT", 10000))

    async def handle(request):
        return web.Response(text="Bot is running!")

    app = web.Application()
    app.add_routes([web.get("/", handle)])

    await asyncio.gather(
        dp.start_polling(bot),
        web._run_app(app, port=PORT)
    )

if __name__ == "__main__":
    asyncio.run(main())
