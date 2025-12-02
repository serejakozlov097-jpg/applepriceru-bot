BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверяем, что токен вообще установлен
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен! Добавь в Environment Variables на Render.")

# Очищаем токен от пробелов и переносов
BOT_TOKEN = BOT_TOKEN.strip()

# Для отладки можно вывести токен в консоль
print("Токен для проверки:", repr(BOT_TOKEN))

# Создаём объект бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
