# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from bankrot_fedresurs.items import BankrotFedresursItem

import xlsxwriter
import string
from datetime import datetime

class BankrotFedresursPipeline:
    def process_item(self, item, spider):
        return item

class XlsxPipeline(object):
    def __init__(self):
        self.bankrot_fedresurs_item = BankrotFedresursItem()
        self.row = 1
        self.col = 0
        self.today_date = datetime.today().strftime("%Y-%m-%d")


    def open_spider(self, spider):
        self.workbook = xlsxwriter.Workbook(filename=f"bankrot_fedresurs_{self.today_date}.xlsx")
        bold = self.workbook.add_format({'bold': 1})
        self.spreadsheet = self.workbook.add_worksheet()
        self.fields = self.bankrot_fedresurs_item.fields.keys()

        self.spreadsheet.write(f"A1", 'Ссылка', bold)
        self.spreadsheet.write(f"B1", 'Номер сообщения', bold)
        self.spreadsheet.write(f"C1", 'Дата публикации', bold)
        self.spreadsheet.write(f"D1", 'Должник', bold)
        self.spreadsheet.write(f"E1", 'Форма аукциона', bold)
        self.spreadsheet.write(f"F1", 'Дата окончания приема заявок', bold)
        self.spreadsheet.write(f"G1", 'Дата торгов', bold)


    def process_item(self, item, spider):
        self.spreadsheet.write(self.row, self.col, item.get('url'))
        self.col += 1
        self.spreadsheet.write(self.row, self.col, item.get('message_number'))
        self.col += 1
        self.spreadsheet.write(self.row, self.col, item.get('publication_date'))
        self.col += 1
        self.spreadsheet.write(self.row, self.col, item.get('debtor'))
        self.col += 1
        self.spreadsheet.write(self.row, self.col, item.get('auction_form'))
        self.col += 1
        self.spreadsheet.write(self.row, self.col, item.get('deadline_for_accepting_applications'))
        self.col += 1
        self.spreadsheet.write(self.row, self.col, item.get('trading_date'))

        self.row += 1
        self.col = 0
        return item


    def close_spider(self, spider):
        self.workbook.close()

