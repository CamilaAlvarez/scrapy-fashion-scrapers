import scrapy
from fashion_scrapper.product_loader import ProductLoader
from fashion_scrapper.items import FashionScrapperItem


class FashionSpider(scrapy.Spider):
    name = 'fashion_spider'
    start_urls = ['https://www.thredup.com']

    def parse(self, response):
        # follow links to paginated products
        for category_url in response.css('a.dropdown-link::attr(href)'):
            yield response.follow(category_url, callback=self.parse_paged_products, meta={'page': 1})

    def parse_paged_products(self, response):
        product_urls = response.css('div.item-card-bottom a::attr(href)')
        if len(product_urls) > 0:
            current_page = response.meta['page']
            next_page = current_page + 1
            url = response.url
            if '?' in url:
                url = url.split('?')[0]
            new_url = '{}?page={}'.format(url, next_page)
            for product_url in product_urls:
                yield response.follow(product_url, callback=self.parse_product_page)
            yield response.follow(new_url, callback=self.parse_paged_products, meta={'page': next_page})

    def parse_product_page(self, response):
        loader = ProductLoader(item=FashionScrapperItem(), response=response)
        loader.add_css('code', 'span[itemprop="productID"]::attr(content)')
        loader.add_css('name', 'h2.item-title[itemprop="name"]::text')
        loader.add_css('description','div.brand-title::text')
        for detail in response.css('div.item-detail-expander div div ul li::text').extract():
            loader.add_value('details', detail)
        for image in response.css('div.thumbnail img::attr(src)').extract():
            if image is not None:
                image = image.replace('thumb','retina')
                loader.add_value('image_urls', image)
        return loader.load_item()

