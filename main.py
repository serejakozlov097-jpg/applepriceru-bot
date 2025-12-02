from aiohttp import web
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ==========================
# Конфигурация и инициализация
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Ошибка: переменная BOT_TOKEN не установлена!")

BOT_TOKEN = BOT_TOKEN.strip()
if "\n" in BOT_TOKEN or "\r" in BOT_TOKEN or " " in BOT_TOKEN:
    raise ValueError(f"BOT_TOKEN содержит недопустимые символы! Проверь токен: {repr(BOT_TOKEN)}")

print("Токен для проверки:", repr(BOT_TOKEN))
print("Длина токена:", len(BOT_TOKEN))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ==========================
# ДАННЫЕ (моды/цвета/память/магазины)
# ==========================
# Модели (код -> отображение)
SMARTPHONES = {
    "iphone16": "iPhone 16",
    "iphone16pro": "iPhone 16 Pro",
    "iphone15promax": "iPhone 15 Pro Max",
}

# Цвета: (код, отображение)
COLORS = [
    ("black", "Черный"),
    ("white", "Белый"),
    ("blue", "Синий"),
]

# Память: (код, отображение)
MEMORY = [
    ("128", "128 GB"),
    ("256", "256 GB"),
    ("512", "512 GB"),
    ("1tb", "1 TB"),
]

# Пример магазинов — можно заменить реальными ссылками/ценами
STORES = [
    ("Restore", "https://restore.ru", "89 990 ₽"),
    ("BigGeek", "https://biggeek.ru", "91 500 ₽"),
    ("re:Store", "https://re-store.ru", "94 990 ₽"),
]

# ==========================
# КОМПОЗИЦИЯ КНОПОК / МЕНЮ
# ==========================
def start_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Смартфоны", callback_data="cat_phones")],
        [InlineKeyboardButton(text="Ноутбуки", callback_data="cat_laptops")],
        [InlineKeyboardButton(text="Планшеты", callback_data="cat_tablets")],
        [InlineKeyboardButton(text="Наушники", callback_data="cat_audio")],
    ])

def smartphone_menu():
    kb = []
    for code, name in SMARTPHONES.items():
        kb.append([InlineKeyboardButton(text=name, callback_data=f"phone_{code}")])
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def color_menu(model_code):
    kb = [
        [InlineKeyboardButton(text=display, callback_data=f"color_{model_code}_{code}")]
        for code, display in COLORS
    ]
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_phones")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def memory_menu(model_code, color_code):
    kb = [
        [InlineKeyboardButton(text=display, callback_data=f"mem_{model_code}_{color_code}_{mcode}")]
        for mcode, display in MEMORY
    ]
    # назад к выбору цвета
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_colors_{model_code}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ==========================
# ХЭНДЛЕРЫ
# ==========================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """
    При /start показываем главное меню (категории).
    """
    await message.answer(
        "Добро пожаловать! 👋\n\nВыберите категорию:",
        reply_markup=start_menu()
    )

# Возврат в стартовое меню
@dp.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=start_menu()
    )

# Категория: смартфоны
@dp.callback_query(F.data == "cat_phones")
async def cat_phones(callback: CallbackQuery):
    await callback.message.edit_text(
        "Смартфоны — выберите модель:",
        reply_markup=smartphone_menu()
    )

# Назад от списка смартфонов в главное меню
@dp.callback_query(F.data == "back_to_phones")
async def back_to_phones(callback: CallbackQuery):
    await callback.message.edit_text(
        "Смартфоны — выберите модель:",
        reply_markup=smartphone_menu()
    )

# Выбор модели (нажатие на конкретный телефон)
@dp.callback_query(F.data.startswith("phone_"))
async def choose_phone(callback: CallbackQuery):
    """
    callback.data = phone_{model_code}
    """
    parts = callback.data.split("_", 1)
    if len(parts) < 2:
        await callback.answer("Неизвестная модель", show_alert=True)
        return
    model_code = parts[1]
    model_name = SMARTPHONES.get(model_code, "Unknown model")
    await callback.message.edit_text(
        f"{model_name}\n\nВыберите цвет:",
        reply_markup=color_menu(model_code)
    )

# Назад: от выбора цвета к списку моделей
@dp.callback_query(F.data.startswith("back_colors_"))
async def back_to_colors(callback: CallbackQuery):
    """
    callback.data = back_colors_{model_code}
    """
    parts = callback.data.split("_", 2)
    # ожидаем parts = ["back","colors","{model_code}"] или ["back","colors","{...}"]
    # но мы формируем "back_colors_{model_code}" -> split by "_" gives ["back","colors","{model_code}"]
    if len(parts) >= 3:
        model_code = parts[2]
    else:
        # на случай несовпадения — вернуть в список смартфонов
        await callback.message.edit_text(
            "Смартфоны — выберите модель:",
            reply_markup=smartphone_menu()
        )
        return

    await callback.message.edit_text(
        "Выберите цвет:",
        reply_markup=color_menu(model_code)
    )

# Выбор цвета
@dp.callback_query(F.data.startswith("color_"))
async def choose_color(callback: CallbackQuery):
    """
    callback.data = color_{model_code}_{color_code}
    """
    parts = callback.data.split("_", 2)
    if len(parts) < 3:
        await callback.answer("Неверные данные", show_alert=True)
        return
    _, model_code, color_code = parts
    model_name = SMARTPHONES.get(model_code, "Unknown model")
    # получить отображаемое имя цвета
    color_display = next((disp for code, disp in COLORS if code == color_code), color_code)
    await callback.message.edit_text(
        f"{model_name}\nЦвет: {color_display}\n\nВыберите объём памяти:",
        reply_markup=memory_menu(model_code, color_code)
    )

# Выбор памяти -> показать ссылки на магазины
@dp.callback_query(F.data.startswith("mem_"))
async def choose_memory(callback: CallbackQuery):
    """
    callback.data = mem_{model_code}_{color_code}_{mem_code}
    """
    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("Неверные данные", show_alert=True)
        return
    _, model_code, color_code, mem_code = parts
    model_name = SMARTPHONES.get(model_code, "Unknown model")
    color_display = next((disp for code, disp in COLORS if code == color_code), color_code)
    mem_display = next((disp for code, disp in MEMORY if code == mem_code), mem_code)

    # Построим сообщение с найденными магазинами (здесь статические данные — подключи парсер/БД по необходимости)
    text = (
        f"📱 {model_name}\n"
        f"🎨 Цвет: {color_display}\n"
        f"💾 Память: {mem_display}\n\n"
        f"🔎 Лучшие предложения по выбранной конфигурации:\n\n"
    )

    for store_name, store_link, store_price in STORES:
        text += f"• {store_name} — {store_price}\n{store_link}\n\n"

    # Кнопки: назад к выбору цвета, в главное меню
    reply_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад (к выбору цвета)", callback_data=f"back_colors_{model_code}")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_start")]
    ])

    await callback.message.edit_text(
        text,
        reply_markup=reply_kb,
        disable_web_page_preview=True
    )

# Заглушки для других категорий (могут быть расширены аналогично смартфонам)
@dp.callback_query(F.data == "cat_laptops")
async def cat_laptops(callback: CallbackQuery):
    await callback.message.edit_text(
        "Категория: Ноутбуки\n\nСкоро здесь появятся модели.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")]
        ])
    )

@dp.callback_query(F.data == "cat_tablets")
async def cat_tablets(callback: CallbackQuery):
    await callback.message.edit_text(
        "Категория: Планшеты\n\nСкоро здесь появятся модели.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")]
        ])
    )

@dp.callback_query(F.data == "cat_audio")
async def cat_audio(callback: CallbackQuery):
    await callback.message.edit_text(
        "Категория: Наушники\n\nСкоро здесь появятся модели.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")]
        ])
    )

# Обновление цен — заглушка
@dp.callback_query(F.data == "refresh")
async def refresh(callback: CallbackQuery):
    await callback.answer("Цены обновляются каждые 15 минут автоматически", show_alert=True)

# ==========================
# Запуск бота + мини-сервер для Render
# ==========================
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
