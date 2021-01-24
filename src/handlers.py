import io
import os
import redis
import random
import logging
from datetime import date, time
from src.frontend import get_image
from src.graphics import process_image
# from decouple import config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)

REF_DATE = date(2017, 10, 22)
SEND_TIME = time(7, 30, 0) # should be 8:30 but timezones suck

r = redis.from_url(os.environ.get("REDIS_URL"))

# Hardcoded stuff, definitely to improve
with io.open('./assets/quotes.txt', 'r', encoding='utf8') as fquotes:
    quotes = fquotes.read().split('\n')
fquotes.close()

# Functions, commands, handler definitions
def start(update, context):
    chat_id = update.effective_chat.id
    if update.effective_chat.type == 'private':
        chat_name = update.effective_chat.username 
    elif update.effective_chat.type == 'group':
        chat_name = update.effective_chat.title 
    else:
        chat_name = 'error'
    r.set(chat_name, chat_id)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Arei qua i fioi')

def subscribe(update, context):
    chat_id = update.effective_chat.id
    if update.effective_chat.type == 'private':
        chat_name = update.effective_chat.username 
    elif update.effective_chat.type == 'group':
        chat_name = update.effective_chat.title 
    else:
        chat_name = 'error'
    if r.exists(chat_name):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Tranquio vecio, te sì zà a posto.')
    else:
        r.set(chat_name, chat_id)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Bravo tosat, apuntamento ałe 8:30.')



def unsubscribe(update, context):
    if update.effective_chat.type == 'private':
        chat_name = update.effective_chat.username 
    elif update.effective_chat.type == 'group':
        chat_name = update.effective_chat.title 
    else:
        chat_name = 'error'
    if r.exists(chat_name):
        r.delete(chat_name)
        context.bot.send_message(chat_id=update.effective_chat.id, text='No va mio ben sta roba, satu? Te convien strucar /segui.')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Varda che te te iera zà cavà via, davero votu eser cussì sicuro de no vedar ła foto?')

def msg_handler(update, context):
    quote_trig(update, context)
    wait_trig(update, context)

def about(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='El bot uficiałe de quei che ghe piaxe el Doxe del Veneto')

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="No go mia capio")

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

# Jobs definition
def daily_image(context):
    img_path = get_image()
    days = (date.today() - REF_DATE).days
    process_image(img_path, str(days))
    db_keys = r.keys(pattern="*")
    for keys in db_keys:
        keys_values = r.get(keys).decode("UTF-8")
        context.bot.send_photo(chat_id=keys_values, photo=open(img_path, 'rb'))
    os.unlink(img_path)

# Message Handlers definition
def quote_trig(update, context):
    if 'zaia' in update.message.text:
        quote=random.choice(quotes)
        context.bot.send_message(chat_id=update.effective_chat.id, text=quote)

def wait_trig(update, context):
    triggers = ['autonomi', 'venet', 'referendum', 'vot']
    for trigger in triggers:
        if trigger in update.message.text:
            days = (date.today() - REF_DATE).days
            text = f"Ennesimo rinvio par la autonomia, è una presa in giro: la misura è colma. Semo {str(days)} giorni in atesa del governo, can del porco!"
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)