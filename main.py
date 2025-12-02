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
# ИНИЦИАЛИЗАЦИЯ БОТА
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Ошибка: переменная BOT_TOKEN не установлена!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ==========================
# ДАННЫЕ
# ==========================

SMARTPHONES = {
    "iphone16": "iPhone 16",
    "iphone16pro": "iPhone 16 Pro",
    "iphone15promax": "iPhone 15 Pro Max"
}

COLORS = ["Черный", "Белый", "Синий"]

MEMORY = ["128GB", "256GB", "512GB", "1TB"]

# Заглушка магазинов (позже можешь подставить реальные данные)
STORES = [
    ("Restore", "https://restore.ru", "89 990 ₽"),
    ("BigGeek", "https://biggeek.ru", "91 500 ₽"),
    ("re:Store", "https://re-store.ru", "94 990 ₽"),
]


# ==========================
# КНОПКИ
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
        [InlineKeyboardButton(text=color, callback_data=f"color_{model_code}_{color}")]
        for color in COLORS
    ]
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_phones")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def memory_menu(model_code, color):
    kb = [
        [InlineKeyboardButton(text=m, callback_data=f"mem_{model_code}_{color}_{m}")]
        for m in MEMORY
    ]
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_colors_{model_code}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


# ==========================
# ОБРАБОТЧИКИ
# ==========================

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Добро пожаловать! 👋\n\nВыберите категорию:",
        reply_markup=start_menu()
    )


# --- Главное меню категорий ---
@dp.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=start_menu()
    )


# --- Категория смартфонов ---
@dp.callback_query(F.data == "cat_phones")
async def cat_phones(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите смартфон:",
        reply_markup=smartphone_menu()
    )


@dp.callback_query(F.data == "back_to_phones")
async def back_to_phones(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите смартфон:",
        reply_markup=smartphone_menu()
    )


# --- Выбор модели ---
@dp.callback_query(F.data.startswith("phone_"))
async def choose_phone(callback: CallbackQuery):
    model_code = callback.data.split("_")[1]
    model_name = SMARTPHONES[model_code]

    await callback.message.edit_text(
        f"Цвет для {model_name}:",
        reply_markup=color_menu(model_code)
    )


@dp.callback_query(F.data.startswith("back_colors_"))
async def back_to_colors(callback: CallbackQuery):
    model_code = callback.data.split("_")[2]

    await callback.message.edit_text(
        "Выберите цвет:",
        reply_markup=color_menu(model_code)
    )


# --- Выбор цвета ---
@dp.callback_query(F.data.startswith("color_"))
async def choose_color(callback: CallbackQuery):
    _, model_code, color = callback.data.split("_")
    model_name = SMARTPHONES[model_code]

    await callback.message.edit_text(
        f"{model_name}\nЦвет: {color}\n\nВыберите память:",
        reply_markup=memory_menu(model_code, color)
    )


# --- Выбор памяти ---
@dp.callback_query(F.data.startswith("mem_"))
async def choose_memory(callback: CallbackQuery):
    _, model_code, color, memory = callback.data.split("_")
    model_name = SMARTPHONES[model_code]

    text = (
        f"📱 {model_name}\n"
        f"🎨 Цвет: {color}\n"
        f"💾 Память: {memory}\n\n"
        f"🔽 Лучшие цены:\n\n"
    )

    for name, link, price in STORES:
        text += f"• {name} — {price}\n{link}\n\n"

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_colors_{model_code}")
