from aiohttp import web
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# --- Токен бота ---
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

# --- Данные для меню ---
CATEGORIES = ["Смартфоны", "Ноутбуки", "Планшеты", "Наушники"]

DEVICES = {
    "Смартфоны": ["iPhone 16", "iPhone 16 Pro", "iPhone 15 Pro Max"],
    "Ноутбуки": ["MacBook Air", "MacBook Pro"],
    "Планшеты": ["iPad Air", "iPad Pro"],
    "Наушники": ["AirPods Pro", "AirPods Max"]
}

COLORS = {
    "iPhone 16": ["Черный", "Белый", "Синий", "Красный"],
    "iPhone 16 Pro": ["Серебристый", "Графитовый", "Золотой", "Синий"],
    "iPhone 15 Pro Max": ["Черный", "Белый", "Синий", "Зеленый"],
    "MacBook Air": ["Серый", "Серебристый", "Золотой"],
    "MacBook Pro": ["Серый", "Серебристый", "Золотой"],
    "iPad Air": ["Розовый", "Серый", "Серебристый", "Зеленый"],
    "iPad Pro": ["Серый", "Серебристый"],
    "AirPods Pro": ["Белый"],
    "AirPods Max": ["Серый", "Синий", "Розовый"]
}

MEMORY = {
    "iPhone 16": ["128GB", "256GB", "512GB"],
    "iPhone 16 Pro": ["128GB", "256GB", "512GB", "1TB"],
    "iPhone 15 Pro Max": ["128GB", "256GB", "512GB"],
    "MacBook Air": ["256GB", "512GB", "1TB"],
    "MacBook Pro": ["512GB", "1TB", "2TB"],
    "iPad Air": ["64GB", "256GB"],
    "iPad Pro": ["128GB", "256GB", "512GB", "1TB"],
    "AirPods Pro": ["—"],
    "AirPods Max": ["—"]
}

# --- Ссылки на магазины ---
SHOP_LINKS = {
    "BigGeek": "https://biggeek.ru/catalog/",
    "reStore": "https://re-store.ru/catalog/",
    "Restore": "https://restore.ru/catalog/",
    "Яндекс Маркет": "https://market.yandex.ru/catalog/",
    "Ozon": "https://www.ozon.ru/category/",
    "Ситилинк": "https://www.citilink.ru/catalog/",
    "МВидео": "https://www.mvideo.ru/products/"
}

# --- Меню клавиатур ---
def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}") for cat in CATEGORIES]
    ])

def devices_keyboard(category):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=dev, callback_data=f"dev_{dev}") for dev in DEVICES[category]],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])

def colors_keyboard(device):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=color, callback_data=f"color_{device}_{color}") for color in COLORS[device]],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_devices_{device}")]
    ])

def memory_keyboard(device, color):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=mem, callback_data=f"mem_{device}_{color}_{mem}") for mem in MEMORY[device]],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_colors_{device}")]
    ])

# --- Обработчики ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Выбери категорию устройства ↓", reply_markup=main_menu_keyboard())

@dp.callback_query(F.data.startswith("cat_"))
async def category_handler(callback: CallbackQuery):
    category = callback.data[4:]
    await callback.message.edit_text(
        f"Выберите устройство в категории {category} ↓",
        reply_markup=devices_keyboard(category)
    )

@dp.callback_query(F.data.startswith("dev_"))
async def device_handler(callback: CallbackQuery):
    device = callback.data[4:]
    await callback.message.edit_text(
        f"Выберите цвет для {device} ↓",
        reply_markup=colors_keyboard(device)
    )

@dp.callback_query(F.data.startswith("color_"))
async def color_handler(callback: CallbackQuery):
    _, device, color = callback.data.split("_", 2)
    await callback.message.edit_text(
        f"Выберите память для {device} ({color}) ↓",
        reply_markup=memory_keyboard(device, color)
    )

@dp.callback_query(F.data.startswith("mem_"))
async def memory_handler(callback: CallbackQuery):
    _, device, color, mem = callback.data.split("_", 3)
    text = f"Выбран товар: {device}\nЦвет: {color}\nПамять: {mem}\n\nСсылки на магазины с минимальными ценами:\n"
    for shop, link in SHOP_LINKS.items():
        device_url = device.lower().replace(" ", "-")
        color_url = color.lower().replace(" ", "-")
        mem_url = mem.lower().replace("gb", "gb")
        text += f"{shop}: {link}{device_url}/{color_url}/{mem_url}\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_colors_{device}")]
    ])
    await callback.message.edit_text(text, reply_markup=kb)

# --- Кнопки "Назад" ---
@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.message.edit_text("Выберите категорию устройства ↓", reply_markup=main_menu_keyboard())

@dp.callback_query(F.data.startswith("back_devices_"))
async def back_devices(callback: CallbackQuery):
    device = callback.data[len("back_devices_"):]
    category = next(cat for cat, devs in DEVICES.items() if device in devs)
    await callback.message.edit_text(
        f"Выберите устройство в категории {category} ↓",
        reply_markup=devices_keyboard(category)
    )

@dp.callback_query(F.data.startswith("back_colors_"))
async def back_colors(callback: CallbackQuery):
    device = callback.data[len("back_colors_"):]
    await callback.message.edit_text(
        f"Выберите цвет для {device} ↓",
        reply_markup=colors_keyboard(device)
    )

# --- Главная функция запуска с мини-сервером для Render ---
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
