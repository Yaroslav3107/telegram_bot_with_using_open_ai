import logging
import sys
import os
from config import TG_BOT_API_KEY
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from utils import load_messages_for_bot, get_image_url
from openapi_client import OpenAIClient
from telegram.constants import ParseMode

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

openai_client = OpenAIClient()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = load_messages_for_bot("main")
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_question = ""
    image_url = get_image_url("chat_gpt")

    if not os.path.exists(image_url):
        logger.error(f"Файл изображения не найден: {image_url}")
        image_url = get_image_url("placeholder") # Использование изображения-заглушки

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

    try:
        with open(image_url, 'rb') as image_file:
            await update.message.reply_photo(image_file, caption="Думаю над відповіддю ... 🤔")
    except Exception as e:
        logger.error(f"Не удалось отправить фото: {e}")

    try:
        response_text = await openai_client.ask(user_question, system_prompt='You are a helpful assistant.')
        await update.message.reply_text(response_text)
    except Exception as e:
        logger.error(f"Помилка під час запиту до OpenAI: {e}")
        await update.message.reply_text(
            "Вибачте, виникла помилка при отриманні відповіді від ChatGPT. Будь ла ласка, спробуйте ще раз пізніше.")

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    image_url = get_image_url("brain")

    if not os.path.exists(image_url):
        logger.error(f"Файл изображения не найден: {image_url}")
        image_url = get_image_url("placeholder")

    try:
        with open(image_url, 'rb') as image_file:
            await update.message.reply_photo(image_file, caption="Шукаю цікавий випадковий факт... 🧠")
    except Exception as e:
        logger.error(f"Не удалось отправить фото: {e}")

    try:
        response_text = await openai_client.ask("Розкажи мені один цікавий факт",
                                                system_prompt='Ти експерт по цікавим фактам')
        await update.message.reply_text(response_text)
    except Exception as e:
        logger.error(f"Помилка при запиті випадкового факту до OpenAI: {e}")
        await update.message.reply_text("Вибачте, не вдалося одержати випадковий факт. Будь ласка, спробуйте ще раз.")

async def talk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    person = " ".join(context.args)
    if not person:
        await update.message.reply_text(
            f"З ким би ви хотіли поговорити? Використовуйте: `/talk Ім'я_особи`. Наприклад: `/talk Альберт Ейнштейн`.",
            parse_mode=ParseMode.MARKDOWN)
        return

    image_url = get_image_url("talk")

    if not os.path.exists(image_url):
        logger.error(f"Файл изображения не найден: {image_url}")
        image_url = get_image_url("placeholder")

    try:
        with open(image_url, 'rb') as image_file:
            await update.message.reply_photo(image_file, caption=f"Починаю розмову з {person}... 👤")
    except Exception as e:
        logger.error(f"Не удалось отправить фото: {e}")

    try:
        response_text = await openai_client.ask(f"Привіт {person}! Розкажи мені щось цікаве про себе чи своє життя",
                                                system_prompt=f"Ти - {person}, відомий вчений/історична особистість/артист. Відповідай як {person}, підтримуючи його/її стиль мови та знання. Будь коротким.")
        await update.message.reply_text(response_text)
    except Exception as e:
        logger.error(f"Помилка при запиті до OpenAI при запиті: {e}")
        await update.message.reply_text("Вибачте, не вдалось розпочати розмову. Спробуйте, будь ласка, пізніше")

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    topic = " ".join(context.args)
    prompt_text = "Придумай одне цікаве питання для вікторини з чотирма варіантами відповіді (A, B, C, D) та вкажи правильну відповідь."
    if topic:
        prompt_text = f"Придумай одне цікаве питання для вікторини на тему '{topic}' з чотирма варіантами відповіді (A, B, C, D) та вкажи правильну відповідь."

    image_url = get_image_url("quiz")

    if not os.path.exists(image_url):
        logger.error(f"Файл изображения не найден: {image_url}")
        image_url = get_image_url("placeholder")

    try:
        with open(image_url, 'rb') as image_file:
            await update.message.reply_photo(image_file, caption="Вигадую питання для вікторини... ❓")
    except Exception as e:
        logger.error(f"Не удалось отправить фото: {e}")

    try:
        response_text = await openai_client.ask(prompt_text, system_prompt="Ти творець вікторин.")
        await update.message.reply_text(response_text)
    except Exception as e:
        logger.error(f"Помилка при запиті до OpenAI при запиті: {e}")
        await update.message.reply_text(
            "Вибачте, що не вдалося згенерувати питання вікторини. Будь ласка, спробуйте ще раз.")

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text_to_translate = " ".join(context.args)
    if not text_to_translate:
        await update.message.reply_text(
            "Будь ласка, вкажіть текст для перекладу після команди /translate."
            "Наприклад: `/translate Hello world`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    image_url = get_image_url("translator")

    if not os.path.exists(image_url):
        logger.error(f"Файл изображения не найден: {image_url}")
        image_url = get_image_url("placeholder")

    try:
        with open(image_url, 'rb') as image_file:
            await update.message.reply_photo(image_file, caption="Перекладаю... 🌐")
    except Exception as e:
        logger.error(f"Не удалось отправить фото: {e}")

    try:
        system_prompt = "Ти - професійний перекладач з англійської на українську та з української на англійську. Відповідай виключно українською мовою."
        response_text = await openai_client.ask(text_to_translate, system_prompt=system_prompt)
        await update.message.reply_text(f"**Переклад:**\n{response_text}", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Помилка під час перекладу: {e}")
        await update.message.reply_text(
            "Вибачте, виникла помилка під час перекладу. Будь ласка, спробуйте ще раз пізніше."
        )

async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    resume_info = " ".join(context.args)
    if not resume_info:
        await update.message.reply_text(
            "Будь ласка, надайте інформацію для резюме після команди /resume."
            "Наприклад: `/resume Ім'я: Іван, Досвід: 5 років програміст, Навички: Python, JS`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    image_url = get_image_url("resume")

    if not os.path.exists(image_url):
        logger.error(f"Файл изображения не найден: {image_url}")
        image_url = get_image_url("placeholder")

    try:
        with open(image_url, 'rb') as image_file:
            await update.message.reply_photo(image_file, caption="Формую резюме... 📄")
    except Exception as e:
        logger.error(f"Не удалось отправить фото: {e}")

    try:
        system_prompt = "Ти - експерт з написання резюме. На основі наданої інформації створи професійне резюме на українській мові. Використовуй заголовки та списки для форматування. Відповідай виключно українською мовою."
        response_text = await openai_client.ask(resume_info, system_prompt=system_prompt)
        await update.message.reply_text(f"**Ваше резюме:**\n{response_text}", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Помилка під час формування резюме: {e}")
        await update.message.reply_text(
            "Вибачте, виникла помилка під час формування резюме. Будь ласка, спробуйте ще раз пізніше."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Update '%s' caused error '%s'", update, context.error)
    if update.effective_message:
        await update.effective_message.reply_text(
            "Відбулася непередбачена помилка. Ми вже працюємо над її усуненням. Будь ласка, спробуйте ще раз пізніше.")

def main() -> None:
    try:
        if not TG_BOT_API_KEY:
            raise ValueError("TG_BOT_API_KEY не встановлено. Будь ласка, перевірте ваш .env файл.")

        app = ApplicationBuilder().token(TG_BOT_API_KEY).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("gpt", gpt_command))
        app.add_handler(CommandHandler("random", random_command))
        app.add_handler(CommandHandler("talk", talk_command))
        app.add_handler(CommandHandler("quiz", quiz_command))
        app.add_handler(CommandHandler("translate", translate_command))
        app.add_handler(CommandHandler("resume", resume_command))

        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_command))

        app.add_error_handler(error_handler)

        logger.info("Бот запущено. Очікування оновлень...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except ValueError as ve:
        logger.critical(f"Критична помилка конфігурації: {ve}")
        logger.critical("Будь ласка, перевірте, що ваш .env файл правильно налаштований та містить TG_BOT_API_KEY.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Критична помилка при запуску бота: {e}",
                        exc_info=True)
        logger.critical("Будь ласка, перевірте змінні середовища (.env файл) та встановлені залежності.")
        sys.exit(1)

if __name__ == '__main__':
    main()
