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
ADMIN_ID = os.getenv("MY_TG_ID")
DEVELOPER_ID = os.getenv("MY_TG_ID")


def scrapy_spider_crawl(scrapy_spider_arguments):
    today = datetime.today().strftime("%Y-%m-%d") 

    bash_command_to_parse = "scrapy crawl lotsSpider" 
    if scrapy_spider_arguments.file_name:
        bash_command_to_parse += f" -a file_name=\"{scrapy_spider_arguments.file_name}\""

    logger.debug(f"START_SPIDER: {bash_command_to_parse}")
    try:
        bash_command = subprocess.check_output(bash_command_to_parse, shell=True)

        excel_table = open(f'bankrot_fedresurs_{today}.xlsx', 'rb')
        excel_table2 = open(f'bankrot_fedresurs_{today}.xlsx', 'rb') 
        bot.send_document(ADMIN_ID, excel_table)
        bot.send_document(DEVELOPER_ID, excel_table2)
        excel_table.close()
        excel_table2.close()
    except Exception as e:
        logger.debug(f"ERROR!!!: {e}")


class UserFilter:
    def __init__(self):
        self.file_name = ''


scrapy_spider_arguments = UserFilter()


@bot.message_handler(commands=['start'])
def get_start(message):
    bot.send_message(ADMIN_ID, text="Готов к работе!")


@bot.message_handler(content_types=['document'])
def process_file(message):
    global scrapy_spider_arguments
    bot.send_message(ADMIN_ID, text="Обработка может занять время...")
    scrapy_spider_arguments.file_name = message.document.file_name

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open(scrapy_spider_arguments.file_name, 'wb') as f:
        f.write(downloaded_file)
   
    bot.send_document(DEVELOPER_ID,downloaded_file)         


@logger.catch
def main():
    bot.polling(none_stop=True)


if __name__ == "__main__":
    main()

    