from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose, Join, TakeFirst


class ProductLoader(ItemLoader):
    code_in = MapCompose(lambda x: x.replace('sku:',''))
    code_out = TakeFirst()
    details_in = MapCompose(str.lower)
    details_out = Join('|')
    name_out = Join()
    description_out = Join()
