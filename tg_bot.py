import logging
import os
from pathlib import Path

from environs import Env
from google.cloud import dialogflow
from telegram import Update, ForceReply, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


logger = logging.getLogger(__name__)


class TelegramLogsHandler(logging.Handler):

    def __init__(self, log_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.log_bot = log_bot
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.setFormatter(formatter)
    def emit(self, record):
        log_entry = self.format(record)
        self.log_bot.send_message(chat_id=self.chat_id, text=log_entry)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def respond(update: Update, context: CallbackContext) -> None:
    """Respond the user message."""
    try:
        session_id = update.effective_user.id
        text = update.message.text
        message_text = detect_intent_text(project_id, session_id, text, language_code="ru")
        update.message.reply_text(message_text)
    except Exception as err:
        logger.exception(err)

def detect_intent_text(project_id, session_id, text, language_code):
    """Returns the result of detect intent with text as input.

    Using the same `session_id` between requests allows continuation
    of the conversation."""

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result.fulfillment_text


def main() -> None:

    updater = Updater(bot_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    GOOGLE_CLOUD_PROJECT = env.str("GOOGLE_CLOUD_PROJECT")
    # BASE_DIR = Path.cwd()
    # GOOGLE_APPLICATION_CREDENTIALS = os.path.join(
    #     BASE_DIR,
    #     env.str("GOOGLE_APPLICATION_CREDENTIALS")
    # )
    project_id = env.str("PROJECT_ID")
    bot_token = env.str("BOT_TOKEN")
    tg_chat_id = env.str("TG_CHAT_ID")
    log_bot_token = env.str('LOG_BOT_TOKEN')
    log_bot = Bot(token=log_bot_token)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(log_bot, tg_chat_id))
    logger.info("Запуск телеграмм бота")
    main()

