import scrapy
from fashion_scrapper.product_loader import ProductLoader
from fashion_scrapper.items import FashionScrapperItem
import math


class BackpackSpider(scrapy.Spider):
    name = 'backpack_spider'
    start_urls = ['https://www.ebags.com/category/backpacks#from0']

    def parse(self, response):
        number_items = int(response.url.split('#')[1].replace('from',''))
        if number_items > 0:
            number_items -= 1
        for backpack_url in response.css('div.listPageImage a::attr(href)'):
            number_items += 1
            yield response.follow(backpack_url, callback=self.parse_backpack_page)
        if number_items <= 2499:
            yield response.follow(response.url.split('#')[0]+'#from'+str(number_items+1), callback=self.parse)

    def parse_backpack_page(self, response):
        loader = ProductLoader(item=FashionScrapperItem(), response=response)
        loader.add_css('code', 'span[id="productDetailModelName"]')
        loader.add_css('name', 'span[id="productDetailModelName"]')
        loader.add_css('details', 'div.productDescription.truncateProductInfo::text')
        for description in response.css('ul.spaced-list.features-list li::text').extract():
            loader.add_value('description', description)
        main_image = response.css('image[id="pdMainImage"]').extract_first()
        main_image = main_image.split('?')[0]
        loader.add_value('image_urls', main_image)
        base_image = '/'.join(main_image.split('/')[:-1])
        for color in response.css('div.img-icon img::attr(src)').extract():
            color_code = color.split('?')[0].split('/')[-1]
            loader.add_value('image_urls', base_image+'/'+color_code)
        return loader.load_item()


