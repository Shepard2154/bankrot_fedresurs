import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from bankrot_fedresurs.items import BankrotFedresursItem
from scrapy_splash import SplashRequest

import time
from datetime import datetime


filter_search_list = {
    'apartment': [
        'Жилое', 'жилое',  
        'Жилой', 'жилой',
        'Жилые', 'жилые',
        'Жилого', 'жилого'
        'Апартаменты', 'апартаменты'
        ],
    'empty': [
        'Магазин', 'магазин',
        'Гостиница', 'гостиница',
        'Сто', 'сто',
        'Станция', 'cтанция',
        'Автосалон', 'автосалон',
        'Отель', 'отель',
        'Мойка', 'мойка',
        'Ангар', 'ангар',
        'Склад', 'склад',
        'Столовая', 'столовая',
        'Павильон', 'павильон',
        'Азс', 'азс',
        'Автозаправочная', 'автозаправочная',
        'Нежилое', 'нежилое'
        ],
    'house': [
        'Садовый', 'садовый'
        ],
    'stead': [
        'Земля', 'земля', 
        'Участок', 'участок', 
        'Земельный', 'земельный',
        'Земельного', 'земельного',
        'Земельному', 'земельному',
        'Земельным', 'земельным',
        'Земельном', 'земельном',
        ]
}


def define_classification(text_data1, text_data2):
    global filter_search_list
    classificated_messages = {
        'apartment': False,
        'empty': False,
        'house': False,
        'stead': False
        }

    all_false_flag = True

    for kind in filter_search_list:
        for keyword in filter_search_list[kind]:
            for row in text_data1:
                if keyword in row.strip().replace('(', '').replace(')', '').replace(',', '').replace('.', '').replace(':', '').replace(';', '').split():
                    classificated_messages[kind] = True
                    print(keyword, " in ", row.strip().replace('(', '').replace(')', '').replace(',', '').replace('.', '').replace(':', '').replace(';', '').split())
            for row in text_data2:
                if keyword in row.strip().replace('(', '').replace(')', '').replace(',', '').replace('.', '').replace(':', '').replace(';', '').split():
                    classificated_messages[kind] = True
                    print(keyword, " in ", row.strip().replace('(', '').replace(')', '').replace(',', '').replace('.', '').replace(':', '').replace(';', '').split())
    
    print("flags: ", classificated_messages)

    for flag in classificated_messages:
        if classificated_messages[flag] == True:
            all_false_flag = False
            return classificated_messages

    return None


class LotsSpider(scrapy.Spider):
    name = 'lotsSpider'
    allowed_domains = ['bankrot.fedresurs.ru']
    GET_lua_script = '''
        function main(splash, args)
            splash.private_mode_enabled = false
            
            url = args.url
            assert(splash:go(url))
            assert(splash:wait(2))
            
            splash:set_viewport_full()

            return {
                html = splash: html()
            }
        end'''
    today_date = datetime.today().strftime("%Y-%m-%d")


    def __init__(self, file_name=None, *args, **kwargs):
        super(LotsSpider).__init__(*args, **kwargs)
        with open(file_name, 'r') as f:
            self.urls = f.read().strip().split('\n')


    def start_requests(self):
        yield SplashRequest(url=self.urls[0], callback=self.parse, endpoint='execute',
                            args={'lua_source': self.GET_lua_script}, meta={'url_number': 1}, dont_filter=True)

        
    def parse(self, response):
        url_number = response.meta['url_number']

        if response.status == 400:
            time.sleep(60*60*1)
            url_number -= 1

        current_url = response.url
        message_number = response.xpath("normalize-space(//table[@class='headInfo']/tbody/tr/td[2]/text())").get()
        publication_date = response.xpath("normalize-space(//table[@class='headInfo']/tbody/tr[2]/td[2]/text())").get()
        debtor = response.xpath("normalize-space(//table[@class='headInfo'][2]/tbody/tr/td[2]/text())").get()
        auction_form = response.xpath("normalize-space(//table[@class='headInfo'][4]/tbody/tr/td[2]/text())").get()
        deadline_for_accepting_applications = response.xpath("normalize-space(//table[@class='headInfo'][4]/tbody/tr[3]/td[2]/text())").get()
        trading_date = response.xpath("normalize-space(//table[@class='headInfo'][4]/tbody/tr[5]/td[2]/text())").get()

        table_lot_info1 = response.xpath("//table[@class='lotInfo']/tbody/tr/td[last()]/text()").getall()
        table_lot_info2 = response.xpath("//table[@class='lotInfo']/tbody/tr/td[2]/text()").getall()

        classification_flags = define_classification(table_lot_info1, table_lot_info2)
        if classification_flags:
            for kind in classification_flags:
                if classification_flags[kind]:
                    loader = ItemLoader(item=BankrotFedresursItem(), response=response)
                    loader.default_output_processor = TakeFirst()
                    loader.add_value("url", current_url)
                    loader.add_value("message_number", message_number)
                    loader.add_value("publication_date", publication_date)
                    loader.add_value("debtor", debtor)
                    loader.add_value("auction_form", auction_form)
                    loader.add_value("deadline_for_accepting_applications", deadline_for_accepting_applications)
                    loader.add_value("trading_date", trading_date)
                    loader.add_value("classification", kind)
                    print("CLASS: ", kind)
                    yield loader.load_item()
        else:
            loader = ItemLoader(item=BankrotFedresursItem(), response=response) 
            loader.default_output_processor = TakeFirst()
            loader.add_value("url", current_url)
            loader.add_value("message_number", message_number)
            loader.add_value("publication_date", publication_date)
            loader.add_value("debtor", debtor)
            loader.add_value("auction_form", auction_form)
            loader.add_value("deadline_for_accepting_applications", deadline_for_accepting_applications)
            loader.add_value("trading_date", trading_date)
            loader.add_value("classification", "other")
            yield loader.load_item()

        if url_number < len(self.urls):
            yield SplashRequest(url=self.urls[url_number], callback=self.parse, endpoint='execute',
                                args={'lua_source': self.GET_lua_script}, meta={'url_number': url_number+1}, dont_filter=True)
