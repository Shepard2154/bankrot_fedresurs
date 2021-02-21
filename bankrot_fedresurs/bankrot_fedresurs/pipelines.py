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

        self.table_row = 1
        self.table_col = 0


    def open_spider(self, spider):
        self.fields = self.bankrot_fedresurs_item.fields.keys()

        self.workbook = xlsxwriter.Workbook(filename=f"bankrot_fedresurs_{self.today_date}.xlsx")
        bold = self.workbook.add_format({'bold': 1})

        self.worksheet = self.workbook.add_worksheet()

        self.worksheet.write(f"A1", 'Ссылка', bold)
        self.worksheet.write(f"B1", 'Номер сообщения', bold)
        self.worksheet.write(f"C1", 'Дата публикации', bold)
        self.worksheet.write(f"D1", 'Должник', bold)
        self.worksheet.write(f"E1", 'Форма аукциона', bold)
        self.worksheet.write(f"F1", 'Дата окончания приема заявок', bold)
        self.worksheet.write(f"G1", 'Дата торгов', bold)
        self.worksheet.write(f"H1", 'Фильтр 1 (квартиры)', bold)
        self.worksheet.write(f"I1", 'Фильтр 2 (коммерция)', bold)
        self.worksheet.write(f"J1", 'Фильтр 3 (участки)', bold)
        self.worksheet.write(f"K1", 'Фильтр 4 (дома)', bold)
        
        

    def process_item(self, item, spider):
        items_keywords = [
            'url', 
            'message_number', 
            'publication_date', 
            'debtor',
            'auction_form',
            'deadline_for_accepting_applications',
            'trading_date',
            'filter_1',
            'filter_2',
            'filter_3',
            'filter_4'
            ]

        for item_keyword in items_keywords:
            self.worksheet.write(self.table_row, self.table_col, item.get(item_keyword))
            self.table_col += 1
        
        self.table_col = 0
        self.table_row += 1

        return item


    def close_spider(self, spider):
        self.workbook.close()

