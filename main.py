from ast import Global
import logging

from binance.spot import Spot
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import telegram  
import time

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

STATE = None
coin = 1
alertnum = 2
alertrange = 3

# Ссылка на api
url = Spot("https://api.binance.com/")

def help_command(update, context):
    update.message.reply_text("Пока в разработке")

def start_command(update, context): 
    keyboard = [
        [
            InlineKeyboardButton("Список алертов", callback_data="list"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(update.effective_message.chat_id, text="Бот для алертов", reply_markup=reply_markup)

def text(update, context):
    global STATE
    
    if STATE == coin:
        return received_coin(update, context)

    if STATE == alertnum:
        return received_alert(update, context)
    
    if STATE == alertrange:
        return get_alert(update, context)

def received_coin(update, context):
    global STATE

    if update.message.text == "<< Вернуться в главное меню":
        return start_command(update, context)

    symbol = str(update.message.text)
        
    context.user_data["coin"] = symbol.upper()
    update.message.reply_text("Write alert")
    STATE = alertnum
        
def received_alert(update, context):
    global STATE
    
    if update.message.text == "<< Вернуться в главное меню":
        return start_command(update, context)
        
    try:
        alert = float(update.message.text)
        context.user_data["alertnum"] = alert
        update.message.reply_text("Write range of alerts")
        STATE = alertrange
    except Exception:
        update.message.reply_text("error")
        return start_command(update, context)

# Получение алертов
def get_alert(update, context):
    global STATE
    
    try:
        if update.message.text == "<< Вернуться в главное меню":
            return start_command(update, context)
                
        symbol = context.user_data["coin"]
        alert = context.user_data["alertnum"]
        rangealerts = int(update.message.text) 
        price = float(url.ticker_price(symbol).get('price'))
        # price_round = 0.1
        # price_rounded = price_round * round(price/price_round)
        # alerts_rounded = price_round * round(alert/price_round)
        # if(alerts_rounded > price_rounded):
        #     if(alerts_rounded <= price_rounded):
        #         update.message.reply_text(price_rounded, " !!!!!")
        # else:
        #     if(alerts_rounded >= price_rounded):
        #         update.message.reply_text(price_rounded, " !!!!!")
        while rangealerts > 0:
            if(alert > price):
                while True:
                    time.sleep(1)
                    price = int(float(url.ticker_price(symbol).get('price')))
                    if(alert <= price):
                        context.bot.send_message(update.message.chat.id, text = f"{price} !!!!!")
                        rangealerts -= 1
                        break
                    else:
                        continue
            else:
                while True:
                    time.sleep(1)
                    price = int(float(url.ticker_price(symbol).get('price')))
                    if(alert >= price):
                        context.bot.send_message(update.message.chat.id, text = f"{price} !!!!!")
                        rangealerts -= 1
                        break  
                    else:
                        continue

        STATE = None
        return start_command(update, context)
    except SyntaxError:
        update.message.reply_text("Symbol not found")
        return start_command(update, context)
     
def inlinebut(update, context):
    global STATE

    query = update.callback_query

    query.answer()
    if query.data == "list":
        keyboard = [
            [InlineKeyboardButton("Создать алерт", callback_data="newalert"), InlineKeyboardButton("Удалить алерт", callback_data="delalert")],
            [InlineKeyboardButton("<< Вернуться в главное меню", callback_data="start")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(text=f"Вот весь список", reply_markup=reply_markup)
    elif query.data == "newalert":  
        STATE = coin
        keyboard = [
                [KeyboardButton("BTCUSDT"), KeyboardButton("ETHUSDT")],
                [KeyboardButton("<< Вернуться в главное меню")],
            ]
        reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        context.bot.send_message(chat_id=update.effective_message.chat_id, text="Напишите название коина", reply_markup=reply_markup) 
    elif query.data == "start":
        return start_command(update, context)     
    
def received_button(update, context):  
    if update.message.text == "<< Вернуться в главное меню":
        return start_command(update, context)
     
def main():
    update = telegram.Update
    
    # Токен бота
    bot = Updater(token=open("data/token.txt", "r").read(), use_context=True)
    
    dispatcher = bot.dispatcher

    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CallbackQueryHandler(inlinebut))
    dispatcher.add_handler(MessageHandler(Filters.text, text))

    bot.start_polling()

    bot.idle()

if __name__ == "__main__":
    main()