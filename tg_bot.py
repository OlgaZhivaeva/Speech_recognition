import logging
import os
from pathlib import Path

from environs import Env
from google.cloud import dialogflow
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


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
    session_id = update.effective_user.id
    text = update.message.text
    message_text = detect_intent_text(project_id, session_id, text, language_code="ru")
    update.message.reply_text(message_text)


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
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(bot_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
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
    main()
