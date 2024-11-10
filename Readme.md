# Speech recognition

The project is designed to create chatbots in Telegram and Vk for speech recognition
using DialogFlou API

### How to install

Clone the repository
```commandline
git clone https://github.com/OlgaZhivaeva/Speech_recognition
```

Create a virtual environment in the project directory and activate it

Python3 should be already installed.

Use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```commandline
pip install -r requirements.txt
```

Create a telegram bot

Create a VK group and get a token from VK API

Create a [project in DialogFlow](https://cloud.google.com/dialogflow/es/docs/quick/setup) and get project ID

Create a [Dialogflow agent](https://cloud.google.com/dialogflow/es/docs/quick/build-agent) for your project

Create a telegram bot for error logging

Create a file `.env` in the project directory:

```commandline
BOT_TOKEN=Your telegram bot token
VK_GROUP_TOKEN=Your VK API token
PROJECT_ID=Your DialogFlow project ID
TG_CHAT_ID=Your Telegram Chat ID
LOG_BOT_TOKEN=Bot token for error logging
```

### Train the DialogFlow agent

[Enable](https://cloud.google.com/dialogflow/es/docs/quick/setup#api) Dialog Flow API

Create DialogFlow API key by running the script run.py
```commandline
python run.py
```

In the project directory, replace the file `training_phrases.json` containing possible questions and
an answer options on your own based on the [sample](https://github.com/OlgaZhivaeva/Speech_recognition/blob/main/training_phrases.json)

Train the agent by running the script `intent.py`
```commandline
python intent.py
```

### Run the bots

```commandline
python tg_bot.py
python vk_bot.py
```

![](https://github.com/OlgaZhivaeva/Speech_recognition/blob/main/demo_tg_bot.gif)


### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).