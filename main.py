from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram

import config
import logging
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

updater = Updater(token=config.BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

bin_endpoint = "http://paste.nushackers.org/documents"

def get_bin_link(key: str) -> str:
    return f"http://paste.nushackers.org/{key}"

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I can be used by typing the /code or /acode command!")

def code(update, context):
    send_code_message(update, context, is_anonymous=False)

def anonymous_code(update, context):
    send_code_message(update, context, is_anonymous=True)


def generate_code_message(a, b):
    return f"*Code Snippet*\n*From:* {a}\n*Link:* {b}\n\nSend spoiler-free code right now with `/code` or `/acode`!"

def send_code_message(update, context, is_anonymous):
    username = update.effective_user.username or ''
    first_name = update.effective_user.first_name or ''
    last_name = update.effective_user.last_name or ''
    name = f"{first_name} {last_name}".strip()
    
    if is_anonymous:
        code_body = update.message.text.replace("/acode", "").replace("@NH_AOC_Bot", "").strip()
    else:
        code_body = update.message.text.replace("/code", "").replace("@NH_AOC_Bot", "").strip()

    if not code_body:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter some code along with your command!\ne.g. `/code console.log(\"Hello World!\");`", parse_mode=telegram.ParseMode.MARKDOWN)
        return

    if is_anonymous:
        displayed_name = "Anonymous"
    elif username:
        displayed_name = f"{name} (@{username})"
    else:
        displayed_name = name
    
    displayed_name = telegram.utils.helpers.escape_markdown(displayed_name)

    try:
        response = requests.post(bin_endpoint, data=code_body)
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Timed out, unable to create paste. Please ping @chrisgzf to ask him to fix.")
        logging.error(response)
        return

    if (response.status_code != 200):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Unable to create paste. Please ping @chrisgzf to ask him to fix.")
        logging.error(response)
        logging.error(response.text)
        return

    key = response.json()["key"]
    bin_url = get_bin_link(key)

    if "group" in update.effective_chat.type:
        # delete original message if sent in group chat
        updater.bot.delete_message(update.effective_chat.id, update.effective_message.message_id)
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=generate_code_message(displayed_name, bin_url), parse_mode=telegram.ParseMode.MARKDOWN)

start_handler = CommandHandler('start', start)
code_handler = CommandHandler('code', code)
anonymous_code_handler = CommandHandler('acode', anonymous_code)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(code_handler)
dispatcher.add_handler(anonymous_code_handler)

updater.start_polling()
