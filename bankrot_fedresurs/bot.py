import sys, os
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
import telebot
from telebot import types


# settings for logging
logger.add("debug.log", format="{time}  {message}", level="DEBUG", rotation="500 MB", compression="zip", encoding='utf-8')

# include .env file
load_dotenv()

bot = telebot.TeleBot(os.getenv("BOT_BANKROT_FEDRESURS"))
ADMIN_ID = os.getenv("ADMIN_TG_ID")
DEVELOPER_ID = os.getenv("MY_TG_ID")

keyboard_menu = types.InlineKeyboardMarkup(row_width=1)
property_category_button = types.InlineKeyboardButton(text='Классификация имущества', callback_data='property_category_query')
search_text_button = types.InlineKeyboardButton(text='Поиск по ключевым словам', callback_data='search_query')
clear_button = types.InlineKeyboardButton(text='Очистить фильтр', callback_data='clear_query')
keyboard_menu.add(property_category_button, search_text_button, clear_button)

keyboard_property_category = types.InlineKeyboardMarkup(row_width=2)
apartment = types.InlineKeyboardButton(text='Квартира', callback_data='apartment')
empty = types.InlineKeyboardButton(text='Нежилое помещение', callback_data='empty')
house = types.InlineKeyboardButton(text='Жилой дом', callback_data='house')
stead = types.InlineKeyboardButton(text='Земельный участок', callback_data='stead')
keyboard_property_category.add(apartment, empty, house, stead)


def scrapy_spider_crawl(scrapy_spider_arguments):
    today = datetime.today().strftime("%Y-%m-%d") 

    bash_command_to_parse = "scrapy crawl lotsSpider" 
    if scrapy_spider_arguments.file_name:
        bash_command_to_parse += f" -a file_name=\"{scrapy_spider_arguments.file_name}\""
    if scrapy_spider_arguments.search_text:
        bash_command_to_parse += f" -a search_text=\"{scrapy_spider_arguments.search_text}\""
    if scrapy_spider_arguments.property_category:
        bash_command_to_parse += f" -a property_category=\"{scrapy_spider_arguments.property_category}\""

    logger.debug(f"START_SPIDER: {bash_command_to_parse}")
    try:
        bash_command = subprocess.check_output(bash_command_to_parse, shell=True)

        excel_table = open(f'bankrot_fedresurs_{today}.xlsx', 'rb')
        excel_table2 = open(f'bankrot_fedresurs_{today}.xlsx', 'rb') 
        bot.send_document(ADMIN_ID, excel_table)
        bot.send_document(DEVELOPER_ID, excel_table2)
        excel_table.close()
        excel_table2.close()
        bot.send_message(ADMIN_ID, text="Хотите установить другие параметры?", reply_markup=keyboard_menu)
    except Exception as e:
        logger.debug(f"ERROR!!!: {e}")


class UserFilter:
    def __init__(self):
        self.property_category = ''
        self.search_text = ''
        self.file_name = ''


    def get_received_text(self, message):
        self.search_text = message.text
        message = bot.send_message(chat_id=ADMIN_ID, text='Принято!')
        bot.edit_message_text(text="Что-то еще настроим? Если готово, то присылайте файл!", chat_id=ADMIN_ID, message_id=message.message_id, reply_markup=keyboard_menu)


    def set_search_text(self, call):
        message = bot.edit_message_text(text="Введите ключевые слова для поиска", chat_id=ADMIN_ID, message_id=call.message.message_id)
        bot.register_next_step_handler(message, self.get_received_text)


scrapy_spider_arguments = UserFilter()


@bot.message_handler(commands=['help', 'start'])
def get_start(message):
    global scrapy_spider_arguments
    bot.send_message(ADMIN_ID, text="Установите параметры фильтра!", reply_markup=keyboard_menu)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global scrapy_spider_arguments
    if call.data == "property_category_query":
        bot.edit_message_text(text="Что-то еще настроим? Если готово, то присылайте файл!", chat_id=ADMIN_ID, message_id=call.message.message_id, reply_markup=keyboard_property_category)
    elif call.data == "search_query":
        scrapy_spider_arguments.set_search_text(call)
    elif call.data == "clear_query":
        scrapy_spider_arguments = UserFilter()
        bot.answer_callback_query(call.id, show_alert=True, text="Вы очистили фильтр!")
        
    elif "apartment" or "empty" or "house" or "stead" == call.data:
        scrapy_spider_arguments.property_category = call.data
        bot.edit_message_text(text="Что-то еще настроим? Если готово, то присылайте файл!", chat_id=ADMIN_ID, message_id=call.message.message_id, reply_markup=keyboard_menu)



@bot.message_handler(content_types=['document'])
def process_file(message):
    global scrapy_spider_arguments
    scrapy_spider_arguments.file_name = message.document.file_name

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open(scrapy_spider_arguments.file_name, 'wb') as f:
        f.write(downloaded_file)
   
    bot.send_document(DEVELOPER_ID,downloaded_file) 
    bot.send_message(ADMIN_ID, text="Принято! Ваш запрос обрабатывается. Это может занять время...")        
    scrapy_spider_crawl(scrapy_spider_arguments)


@logger.catch
def main():
    bot.polling(none_stop=True, interval=1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        bot.stop_polling()
        bot.polling(none_stop=True, interval=1)

    
while True:
    pass
