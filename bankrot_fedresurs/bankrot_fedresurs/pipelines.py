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
        self.today_date = datetime.today().strftime('%Y-%m-%d')

        self.row_worksheet_apartment = 1
        self.row_worksheet_empty = 1
        self.row_worksheet_house = 1
        self.row_worksheet_stead = 1
        self.row_worksheet_other = 1

        self.rows = {
            'apartment': self.row_worksheet_apartment, 
            'empty':self.row_worksheet_empty, 
            'house': self.row_worksheet_house, 
            'stead': self.row_worksheet_stead,
            'other': self.row_worksheet_other,
        }

        self.col_worksheet_apartment = 0
        self.col_worksheet_empty = 0
        self.col_worksheet_house = 0
        self.col_worksheet_stead = 0
        self.col_worksheet_other = 0

        self.cols = {
            'apartment': self.col_worksheet_apartment, 
            'empty':self.col_worksheet_empty, 
            'house': self.col_worksheet_house, 
            'stead': self.col_worksheet_stead,
            'other': self.col_worksheet_other,
        }


    def open_spider(self, spider):
        self.fields = self.bankrot_fedresurs_item.fields.keys()

        self.workbook = xlsxwriter.Workbook(filename=f"bankrot_fedresurs_{self.today_date}.xlsx")
        bold = self.workbook.add_format({'bold': 1})

        self.worksheet_apartment = self.workbook.add_worksheet()
        self.worksheet_empty = self.workbook.add_worksheet()
        self.worksheet_house = self.workbook.add_worksheet()
        self.worksheet_stead = self.workbook.add_worksheet()
        self.worksheet_other = self.workbook.add_worksheet()

        self.worksheets = {
            'apartment': self.worksheet_apartment, 
            'empty':self.worksheet_empty, 
            'house': self.worksheet_house, 
            'stead': self.worksheet_stead,
            'other': self.worksheet_other,
        }

        for worksheet in self.worksheets.values():
            worksheet.write(f"A1", 'Ссылка', bold)
            worksheet.write(f"B1", 'Номер сообщения', bold)
            worksheet.write(f"C1", 'Дата публикации', bold)
            worksheet.write(f"D1", 'Должник', bold)
            worksheet.write(f"E1", 'Форма аукциона', bold)
            worksheet.write(f"F1", 'Дата окончания приема заявок', bold)
            worksheet.write(f"G1", 'Дата торгов', bold)


    def process_item(self, item, spider):
        classification = item.get('classification')
        items_keywords = [
            'url', 
            'message_number', 
            'publication_date', 
            'debtor',
            'auction_form',
            'deadline_for_accepting_applications',
            'trading_date'
            ]

        for item_keyword in items_keywords:
            self.worksheets[classification].write(self.rows[classification], self.cols[classification], item.get(item_keyword))
            self.cols[classification] += 1

        self.rows[classification] += 1
        self.cols[classification] = 0

        return item


    def close_spider(self, spider):
        self.workbook.close()

