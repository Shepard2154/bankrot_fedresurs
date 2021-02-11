import scrapy


class BankrotFedresursItem(scrapy.Item):
    url = scrapy.Field()
    message_number = scrapy.Field()
    publication_date = scrapy.Field()
    debtor = scrapy.Field()
    auction_form = scrapy.Field()
    deadline_for_accepting_applications = scrapy.Field()
    trading_date = scrapy.Field()
    classification = scrapy.Field()