# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BankrotFedresursItem(scrapy.Item):
    url = scrapy.Field()
    message_number = scrapy.Field()
    publication_date = scrapy.Field()
    debtor = scrapy.Field()
    auction_form = scrapy.Field()
    deadline_for_accepting_applications = scrapy.Field()
    trading_date = scrapy.Field()