import scrapy
from fashion_scrapper.product_loader import ProductLoader
from fashion_scrapper.items import FashionScrapperItem
import math


class AsosSpider(scrapy.Spider):
    name = 'asos_spider'
    start_urls = ['http://us.asos.com/']

    def parse(self, response):
        for category_column in response.css('ul.items'):
            for category_url in category_column.css('li a::attr(href)'):
                yield response.follow(category_url, callback=self.parse_category_page, meta={'page_number':0})

    def parse_category_page(self, response):
        page_url = response.url
        if 'women' in page_url:
            page_number = response.meta['page_number']
            if page_number == 0:
                total_page_number_selector = response.css('span.total-results::text').extract()
                if len(total_page_number_selector) > 0:
                    page_size = 36
                    total_page_number_string = total_page_number_selector[0].replace(',','')
                    total_page_number = int(math.ceil(int(total_page_number_string)*1./page_size))
                else:
                    total_page_number = 1
            else:
                total_page_number = response.meta['total_pages']
            metadata = {'page_number': page_number +1,
                        'total_pages': total_page_number}

            if page_number + 1 < total_page_number:
                new_url = page_url.replace('&pge={}'.format(page_number), '')
                new_url = '{}&pge={}'.format(new_url, page_number + 1)
                yield response.follow(new_url, callback=self.parse_category_page, meta=metadata)


            for product in response.css('a.product.product-link::attr(href)').extract():
                yield response.follow(product, callback=self.parse_product)

    def parse_product(self, response):
        loader = ProductLoader(item=FashionScrapperItem(), response=response)
        loader.add_css('code', 'div.product-code span::text')
        loader.add_css('name', 'div.product-hero h1::text')
        loader.add_css('details', 'div.about-me span::text')
        for description in response.css('div.product-description span ul li::text').extract():
            loader.add_value('description', description)
        for image in response.css('li.image-thumbnail a img::attr(src)').extract():
            image_parts = image.split('?')
            image = image_parts[0]
            image = '{}?$XXL$'.format(image)
            loader.add_value('image_urls', image)
        return loader.load_item()


