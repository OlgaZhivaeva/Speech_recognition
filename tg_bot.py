import logging

from environs import Env
from telegram import Update, ForceReply, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from detect_intent_text import detect_intent_text
from log_handler import TelegramLogsHandler


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def main() -> None:
    def respond(update: Update, context: CallbackContext) -> None:
        """Respond the user message."""
        try:
            session_id = update.effective_user.id
            text = update.message.text
            message_text = detect_intent_text(project_id, session_id, text, language_code="ru")
            update.message.reply_text(message_text.fulfillment_text)
        except Exception as err:
            logger.exception(err)

    env = Env()
    env.read_env()
    GOOGLE_CLOUD_PROJECT = env.str("GOOGLE_CLOUD_PROJECT")
    GOOGLE_APPLICATION_CREDENTIALS = env.str("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = env.str("PROJECT_ID")
    bot_token = env.str("TELEGRAM_BOT_TOKEN")
    tg_chat_id = env.str("TG_CHAT_ID")
    log_bot_token = env.str('LOG_BOT_TOKEN')
    log_bot = Bot(token=log_bot_token)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(log_bot, tg_chat_id))
    logger.info("Запуск телеграмм бота")
    updater = Updater(bot_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
