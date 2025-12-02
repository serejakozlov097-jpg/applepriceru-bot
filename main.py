from aiohttp import web
import asyncio
import logging
import os
import random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# Получаем токен
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен!")
BOT_TOKEN = BOT_TOKEN.strip()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# ----------- ЛИНЕЙКИ ------------
IPHONE_LINES = {
    "line15": "IPHONE 15",
    "line16": "IPHONE 16",
    "line17": "IPHONE 17"
}

# ----------- ВСЕ МОДЕЛИ ----------------
IPHONE_MODELS = {
    # Линейка 15
    "iphone15": {"line": "line15", "name": "iPhone 15"},
    "iphone15plus": {"line": "line15", "name": "iPhone 15 Plus"},
    "iphone15pro": {"line": "line15", "name": "iPhone 15 Pro"},
    "iphone15promax": {"line": "line15", "name": "iPhone 15 Pro Max"},

    # Линейка 16
    "iphone16": {"line": "line16", "name": "iPhone 16"},
    "iphone16plus": {"line": "line16", "name": "iPhone 16 Plus"},
    "iphone16pro": {"line": "line16", "name": "iPhone 16 Pro"},
    "iphone16promax": {"line": "line16", "name": "iPhone 16 Pro Max"},

    # Линейка 17
    "iphone17": {"line": "line17", "name": "iPhone 17"},
    "iphone17air": {"line": "line17", "name": "iPhone 17 Air"},
    "iphone17pro": {"line": "line17", "name": "iPhone 17 Pro"},
    "iphone17promax": {"line": "line17", "name": "iPhone 17 Pro Max"},
}

# ----------- Опции памяти и цвета (общие для всех моделей) -----------

MEMORY_OPTIONS = {
    "128GB": {"ЯндексМаркет": "...", "Ozon": "..."},
    "256GB": {"ЯндексМаркет": "...", "Ozon": "..."},
    "512GB": {"ЯндексМаркет": "...", "Ozon": "..."},
    "1TB": {"ЯндексМаркет": "...", "Ozon": "..."}
}

COLORS = ["Черный", "Белый", "Синий", "Красный", "Золотой", "Серый"]

# ---------- Клавиатуры ---------

def get_lines_menu():
    """Меню выбора линейки iPhone"""
    keyboard = []
    for code, name in IPHONE_LINES.items():
        keyboard.append([InlineKeyboardButton(text=name, callback_data=f"line_{code}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_models_menu(line_code):
    """Меню моделей внутри выбранной линейки"""
    keyboard = []
    suffix = str(random.randint(1, 999999))

    for model_code, info in IPHONE_MODELS.items():
        if info["line"] == line_code:
            keyboard.append([
                InlineKeyboardButton(
                    text=info["name"],
                    callback_data=f"model_{model_code}_{suffix}"
                )
            ])

    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_lines")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_memory_menu(model_code):
    keyboard = []

    for mem in MEMORY_OPTIONS.keys():
        keyboard.append([
            InlineKeyboardButton(
                text=mem,
                callback_data=f"memory_{model_code}_{mem}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_models_{model_code}")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ---------------- Команды ----------------

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Выберите линейку iPhone", reply_markup=get_lines_menu())


# ---------------- Обработчики ----------------

@dp.callback_query(F.data.startswith("line_"))
async def choose_line(callback: CallbackQuery):
    line_code = callback.data.split("_")[1]

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        f"Выберите модель из линейки {IPHONE_LINES[line_code]}",
        reply_markup=get_models_menu(line_code)
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("model_"))
async def select_model(callback: CallbackQuery):
    parts = callback.data.split("_")
    model_code = parts[1]

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        f"Вы выбрали {IPHONE_MODELS[model_code]['name']}. Выберите объём памяти:",
        reply_markup=get_memory_menu(model_code)
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("back_to_models_"))
async def back_to_models(callback: CallbackQuery):
    model_code = callback.data.replace("back_to_models_", "")
    line_code = IPHONE_MODELS[model_code]["line"]

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        f"Выберите модель из линейки {IPHONE_LINES[line_code]}",
        reply_markup=get_models_menu(line_code)
    )
    await callback.answer()


@dp.callback_query(F.data == "back_to_lines")
async def back_to_lines(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer("Выберите линейку iPhone", reply_markup=get_lines_menu())
    await callback.answer()


@dp.callback_query(F.data.startswith("memory_"))
async def select_memory(callback: CallbackQuery):
    _, model_code, mem = callback.data.split("_", 2)

    model_name = IPHONE_MODELS[model_code]["name"]

    text = f"Ссылки на {model_name} {mem}:\n\n"
    for shop, link in MEMORY_OPTIONS[mem].items():
        text += f"{shop} ({random.choice(COLORS)}): {link}\n"

    text += "\nНажмите «⬅️ Назад», чтобы выбрать другой вариант."

    try:
        await callback.message.delete()
    except:
        pass

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_models_{model_code}")]
    ])

    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


# ------------ Мини-сервер для Render -------------
async def main():
    logging.info("Бот запускается...")
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
