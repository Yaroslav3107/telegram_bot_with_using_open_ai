from config import TG_BOT_API_KEY
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, Updater
from utils import load_messages_for_bot
from openapi_client import OpenAIClient
from telegram.constants import ParseMode
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

openai_client = OpenAIClient()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = load_messages_for_bot("main")
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_question =""
    if update.message.text.startswith("/gpt") and context.args:
        user_question = " ".join(context.args)
    elif update.message.text.strip() == '/gpt':
        await update.message.reply_text(
            "Будь ласка, поставте запитання після команди /gpt."
            "Наприклад: `/gpt Як приготувати борщ?`\n"
            "Або просто напишіть мені повідомлення, і я відповім.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    else:
        user_question = update.message.text
    if not user_question:
        await update.message.reply_text("Будь ласка, поставте запитання.", parse_mode=ParseMode.MARKDOWN)
        return
    await update.message.reply_text("Думаю над відповіддю ... 🤔")

    try:
        response_text = openai_client.ask(user_question,system_prompt = 'You are a helpful assistant.')
        await update.message.reply_text(response_text)
    except Exception as e:
        logger.error(f"Помилка під час запиту до OpenAI: {e}")
        await update.message.reply_text("Вибачте, виникла помилка при отриманні відповіді від ChatGPT. Будь ласка, спробуйте ще раз пізніше.")

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Шукаю цікавий випадковий факт... 🧠")
    try:
        response_text = await openai_client.ask("Розкажи мені один цікавий факт", system_prompt = 'Ти експерт по цікавим фактам')
        await update.message.reply_text(response_text)
    except Exception as e:
        logger.error(f"Помилка при запиті випадкового факту до OpenAI: {e}")
        await update.message.reply_text("Вибачте, не вдалося одержати випадковий факт. Будь ласка, спробуйте ще раз.")

async def talk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    person = " ".join(context.args)
    if not person:
        await update.message.reply_text(f"З ким би ви хотіли поговорити? Використовуйте: `/talk Ім'я_особи`. Наприклад: `/talk Альберт Ейнштейн`.", parse_mode=ParseMode.MARKDOWN)
        return

    await update.message.reply_text(f"Начинаю розмову з {person}... 👤")
    try:
        response_text = await openai_client.ask(f"Привіт {person}! Розкажи мені щось цікаве про себе чи своє життя", system_prompt=f"Ти - {person}, відомий вчений/історична особистість/артист. Відповідай як {person}, підтримуючи його/її стиль мови та знання. Будь коротким.")
        await update.message.reply_text(response_text)
    except Exception as e:
        logger.error(f"Помилка при запиті до OpenAI при запиті: {e}")
        await update.message.reply_text("Вибачте, не вдалось розпочати розмову. Спробуйте, будт-ласка, пізніше")

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    topic = " ".join(context.args)
    prompt_text = "Придумай одне цікаве питання для вікторини з чотирма варіантами відповіді (A, B, C, D) та вкажи правильну відповідь."
    if topic:
        prompt_text = f"Придумай одне цікаве питання для вікторини на тему '{topic}' з чотирма варіантами відповіді (A, B, C, D) та вкажи правильну відповідь."

    await update.message.reply_text("Вигадую питання для вікторини... ❓")
    try:
        response_text = await openai_client.ask(prompt_text, system_prompt="Ти творець вікторин.")
        await update.message.reply_text(response_text)
    except Exception as e:
        logger.error(f"Помилка при запиті до OpenAI при запиті: {e}")
        await update.message.reply_text("Вибачте, що не вдалося згенерувати питання вікторини. Будь ласка, спробуйте ще раз.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Update '%s' caused error '%s'", update, context.error)
    if update.effective_message:
        await update.message.reply_text("Відбулася непередбачена помилка. Ми вже працюємо над її усуненням. Будь ласка, спробуйте пізніше.")

def main() -> None:
    """Запускает бота."""
    try:
        app = ApplicationBuilder().token(TG_BOT_API_KEY).build()

        # Добавляем обработчики команд
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("gpt", gpt_command)) # Явная команда /gpt
        app.add_handler(CommandHandler("random", random_command))
        app.add_handler(CommandHandler("talk", talk_command)) # Возвращен к простому CommandHandler
        app.add_handler(CommandHandler("quiz", quiz_command))

        # Добавляем обработчик для ЛЮБЫХ текстовых сообщений, которые НЕ являются командами.
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_command))

        # Добавляем обработчик ошибок
        app.add_error_handler(error_handler)

        # Запускаем бота
        logger.info("Бот запущен. Ожидание обновлений...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске бота: {e}")
        logger.critical("Пожалуйста, проверьте переменные окружения (.env файл) и установленные зависимости.")
        sys.exit(1)

# app = ApplicationBuilder().token(TG_BOT_API_KEY).build()
# app.add_handler(CommandHandler("start", start))
# app.run_polling()