import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from bankrot_fedresurs.items import BankrotFedresursItem
from scrapy_splash import SplashRequest

from datetime import datetime


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

    filter_search_list = {
        'apartment': [
            'Жилое', 
            'Апартаменты'
            ],
        'empty': [
            'Магазин',
            'Гостиница',
            'Сто',
            'Станция тех. Обслуживания',
            'Автосалон',
            'Здание',
            'Здания',
            'Отель',
            'Мойка',
            'Ангар',
            'Склад',
            'Столовая',
            'Павильон',
            'Азс',
            'Автозаправочная станция'
            ],
        'house': [
            'Садовый дом'
            ],
        'stead': [
            'Земля'
            ]
    }


    def __init__(self, property_category=None, search_text=None, file_name=None, *args, **kwargs):
        super(LotsSpider).__init__(*args, **kwargs)

        self.property_category = property_category
        self.search_text = search_text
        with open(file_name, 'r') as f:
            self.urls = f.read().strip().split('\n')\
    

    def start_requests(self):
        yield SplashRequest(url=self.urls[0], callback=self.parse, endpoint='execute',
                            args={'lua_source': self.GET_lua_script}, meta={'url_number': 1})

        
    def parse(self, response):
        url_number = response.meta['url_number']

        loader = ItemLoader(item=BankrotFedresursItem(), response=response)
        loader.default_output_processor = TakeFirst()

        current_url = response.url
        message_number = response.xpath("normalize-space(//table[@class='headInfo']/tbody/tr/td[2]/text())").get()
        publication_date = response.xpath("normalize-space(//table[@class='headInfo']/tbody/tr[2]/td[2]/text())").get()
        debtor = response.xpath("normalize-space(//table[@class='headInfo'][2]/tbody/tr/td[2]/text())").get()
        auction_form = response.xpath("normalize-space(//table[@class='headInfo'][4]/tbody/tr/td[2]/text())").get()
        deadline_for_accepting_applications = response.xpath("normalize-space(//table[@class='headInfo'][4]/tbody/tr[3]/td[2]/text())").get()
        trading_date = response.xpath("normalize-space(//table[@class='headInfo'][4]/tbody/tr[5]/td[2]/text())").get()

        search_text_flag = False
        property_category_flag = False

        if self.search_text:
            table_lot_info = response.xpath("//table[@class='lotInfo']/tbody/tr/td[2]/text()").getall()
            print(table_lot_info)
            for row in table_lot_info:
                if self.search_text in row:
                    search_text_flag = True

        if self.property_category:
            table_lot_info = response.xpath("//table[@class='lotInfo']/tbody/tr/td[last()]/text()").getall()
            for i in range(len(table_lot_info)):
                print(i, table_lot_info[i])
            print(len(table_lot_info))
            keywords_filter = self.filter_search_list.get(self.property_category)
            for keyword in keywords_filter:
                for row in table_lot_info:
                    if keyword in row:
                        property_category_flag = True
                        break
        
        if (self.search_text and search_text_flag and self.property_category and property_category_flag) or (self.search_text==self.property_category==None) or (self.search_text and search_text_flag and self.property_category==None) or (self.property_category and property_category_flag and self.search_text==None):
            loader.add_value("url", current_url)
            loader.add_value("message_number", message_number)
            loader.add_value("publication_date", publication_date)
            loader.add_value("debtor", debtor)
            loader.add_value("auction_form", auction_form)
            loader.add_value("deadline_for_accepting_applications", deadline_for_accepting_applications)
            loader.add_value("trading_date", trading_date)

            yield loader.load_item()

        if url_number < len(self.urls):
            yield SplashRequest(url=self.urls[url_number], callback=self.parse, endpoint='execute',
                                args={'lua_source': self.GET_lua_script}, meta={'url_number': url_number+1})
