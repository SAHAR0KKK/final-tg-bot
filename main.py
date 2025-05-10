import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в .env файле")
if not ADMIN_GROUP_ID:
    raise RuntimeError("ADMIN_GROUP_ID не задан в .env файле")

try:
    ADMIN_GROUP_ID = int(ADMIN_GROUP_ID)
except ValueError:
    raise ValueError("ADMIN_GROUP_ID должен быть числом")

logging.basicConfig(level=logging.INFO)

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Информация", callback_data="info")]
    ])
    await update.message.reply_text("Привет! Я бот для обратной связи.", reply_markup=keyboard)
    if update.effective_user:
        name = update.effective_user.full_name
        await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=f"{name} запустил бота.")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Просто напиши мне сообщение, и я передам его администрации.")

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ответить", callback_data=f"reply:{user.id}")]
    ])
    await context.bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text=f"Сообщение от {user.full_name}:
{text}",
        reply_markup=keyboard
    )
    await update.message.reply_text("Ваше сообщение отправлено администрации.")

# Обработка нажатий кнопок
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("reply:"):
        user_id = int(query.data.split(":")[1])
        await context.bot.send_message(chat_id=user_id, text="Админ получил ваше сообщение и скоро ответит.")

# Запуск приложения
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
