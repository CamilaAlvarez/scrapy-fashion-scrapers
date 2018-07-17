import scrapy
from fashion_scrapper.product_loader import ProductLoader
from fashion_scrapper.items import FashionScrapperItem
import math


class TradesySpider(scrapy.Spider):
    name = 'tradesy_spider'
    base_url = 'https://www.tradesy.com/'
    start_urls = [base_url]

    def parse(self, response):
        for idx, category_section in enumerate(response.css('ul.trd-menu > li')):
            if idx < 2:
                continue
            main_category_name = category_section.css('a.toplevel::text').extract_first()
            category_column = category_section.css('div.trd-dropdown > ul')
            if len(category_column) == 0:
               print('Got to an unaccessible category: {}'.format(category_section.css('a::text').extract_first()))
               continue
            for category in category_column[0].css('li > a'):
                category_class = category.xpath('@class').extract_first()
                if category_class == 'view' or category_class == 'primary':
                    continue
                category_url = category.xpath('@href').extract_first()
                category_name = category.xpath('text()').extract_first().strip()
                yield response.follow(category_url, callback=self.parse_category_page,
                                      meta={'categories': [main_category_name, category_name]})

    def parse_category_page(self, response):
        subcategories = response.css('div[id="department-filters"] > ul[id="filters-nested"] > li > ul.indent > li > '
                                     'ul.indent > li > a')
        if len(subcategories) > 0:
            for subcategory in subcategories:
                subcategory_url = subcategory.xpath('@href')
                subcategory_name = subcategory.xpath('@data-value').extract_first()
                yield response.follow('{}{}'.format(self.base_url, subcategory_url),
                                      callback=self.parse_category_page,
                                      meta={'categories':  response.meta['categories'] + [subcategory_name]})
        else:
            current_page_str = response.css('li.page-link span.active::text').extract_first()
            current_page = int(current_page_str)
            total_page_number_selector = response.css('li.page-link > a')
            total_page_number_str = response.css('li.page-link > a::attr(href)')
            if len(total_page_number_str.extract_first().split('?page=')) == 1:
                total_page_number_str = 1
            elif len(total_page_number_selector[-1].css('span')) == 0:
                total_page_number_str = total_page_number_selector[-1].xpath('//text()').extract_first()
            else:
                total_page_number_str = total_page_number_str.extract()[-1].split('?page=')[1]
            total_page_number = int(total_page_number_str)
            products = response.css('a.item-image::attr(href)').extract()
            for product in products:
                product_url = '{}{}'.format(self.base_url, product)
                yield response.follow(product_url, callback=self.parse_product,
                                      meta=response.meta)
            if current_page < total_page_number:
                next_page_url = response.url.split('?')[0]
                next_page_url = next_page_url + '?page=' + str(current_page + 1)
                yield response.follow(next_page_url, callback=self.parse_category_page, meta=response.meta)


    def parse_product(self, response):
        loader = ProductLoader(item=FashionScrapperItem(), response=response)
        code = response.css('span.item-id::text').extract_first().replace('Item #:','').strip()
        loader.add_value('code', code)
        loader.add_css('name', 'span[id="idp-title"]::text')
        loader.add_css('description', 'p[itemprop="description"]::text')
        loader.add_css('details', 'div.idp-details.idp-info-accordion > div::text')
        for idx, image in enumerate(response.css('div.idp-thumbnail-slider div.inner > ul > li > div > img.thumb::attr(src)')
                                            .extract()):
            image_parts = image.split('?')
            image = image_parts[0]
            loader.add_value('image_urls', image)
        for category in response.meta['categories']:
            loader.add_value('categories', category)
        return loader.load_item()


