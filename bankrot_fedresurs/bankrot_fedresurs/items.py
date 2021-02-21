import scrapy


class BankrotFedresursItem(scrapy.Item):
    url = scrapy.Field()
    message_number = scrapy.Field()
    publication_date = scrapy.Field()
    debtor = scrapy.Field()
    auction_form = scrapy.Field()
    deadline_for_accepting_applications = scrapy.Field()
    trading_date = scrapy.Field()
    filter_1 = scrapy.Field() 
    filter_2 = scrapy.Field()
    filter_3 = scrapy.Field()
    filter_4 = scrapy.Field()