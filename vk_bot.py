import logging
import random

import vk_api as vk
import telegram

from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType

from detect_intent_text import detect_intent_text
from log_handler import TelegramLogsHandler


def respond(event, vk_api):
    try:
        message = detect_intent_text(project_id=project_id, session_id=event.user_id, text=event.text, language_code="ru")
        if not message.intent.is_fallback:
            vk_api.messages.send(
                user_id=event.user_id,
                message=message.fulfillment_text,
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
    GOOGLE_APPLICATION_CREDENTIALS = env.str("GOOGLE_APPLICATION_CREDENTIALS")
    vk_group_token = env.str('VK_GROUP_TOKEN')
    tg_chat_id = env.str('TG_CHAT_ID')
    log_bot_token = env.str('LOG_BOT_TOKEN')

    log_bot = telegram.Bot(token=log_bot_token)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(log_bot, tg_chat_id))
    logger.info("Запуск vk бота")
    vk_session = vk.VkApi(token=vk_group_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            respond(event, vk_api)
