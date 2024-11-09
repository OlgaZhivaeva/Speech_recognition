import logging
import random

import vk_api as vk
import telegram

from environs import Env
from google.cloud import dialogflow
from vk_api.longpoll import VkLongPoll, VkEventType


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
    if not response.query_result.intent.is_fallback:
        return response.query_result.fulfillment_text


def respond(event, vk_api):
    try:
        message = detect_intent_text(project_id=project_id, session_id=event.user_id, text=event.text, language_code="ru")
        if message:
            vk_api.messages.send(
                user_id=event.user_id,
                message=message,
                random_id=random.randint(1,1000)
            )
            logger.info("Бот ответил")
        else:
            logger.info("Бот не может ответить")
    except Exception as err:
        logger.exception(err)


if __name__ == "__main__":

    env = Env()
    env.read_env()
    project_id = env.str("PROJECT_ID")
    GOOGLE_CLOUD_PROJECT = env.str("GOOGLE_CLOUD_PROJECT")
    vk_group_token = env.str('VK_GROUP_TOKEN')
    tg_chat_id = env.str('TG_CHAT_ID')
    log_bot_token = env.str('LOG_BOT_TOKEN')

    log_bot = telegram.Bot(token=log_bot_token)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(log_bot, tg_chat_id))
    logger.info("Запуск бота")
    vk_session = vk.VkApi(token=vk_group_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            respond(event, vk_api)
