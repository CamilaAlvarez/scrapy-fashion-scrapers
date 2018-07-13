import scrapy
from fashion_scrapper.product_loader import ProductLoader
from fashion_scrapper.items import FashionScrapperItem
import math


class BackpackSpider(scrapy.Spider):
    name = 'backpack_spider'
    start_urls = ['https://www.ebags.com/category/backpacks#from0']

    def parse(self, response):
        return self.parse_items_page(response)

    def parse_items_page(self, response):
        page_size = 119
        if 'page' not in response.meta:
            page = 0
        else:
            page = response.meta['page']
        if page <= 21:
            yield response.follow(response.url.split('#')[0]+'#from'+str((page+1)*page_size ), callback=self.parse_items_page, dont_filter = True, meta={'page': page +1,
                                        'splash': {
                                            'args': {
                                                # set rendering arguments here
                                                'html': 1
                                            },
                                            'endpoint': 'render.html'
                                        }
                                        })
        for backpack_url in response.css('div.listPageImage a::attr(href)'):
            yield response.follow(backpack_url, callback=self.parse_backpack_page, dont_filter=True, meta={
                                        'splash': {
                                            'args': {
                                                # set rendering arguments here
                                                'html': 1
                                            },
                                            'endpoint': 'render.html'
                                        }
                                        })


    def parse_backpack_page(self, response):
        print(response.url)
        loader = ProductLoader(item=FashionScrapperItem(), response=response)
        loader.add_css('code', 'span[id="productDetailModelName"]::text')
        loader.add_css('name', 'span[id="productDetailModelName"]::text')
        loader.add_css('details', 'div.productDescription.truncateProductInfo::text')
        for description in response.css('ul.spaced-list.features-list li::text').extract():
            loader.add_value('description', description)
        main_image = response.css('img[id="pdMainImage"]::attr(src)').extract_first()
        main_image = main_image.split('?')[0]
        loader.add_value('image_urls', main_image)
        base_image = '/'.join(main_image.split('/')[:-1])
        for color in response.css('div.img-icon img::attr(src)').extract():
            color_code = color.split('?')[0].split('/')[-1]
            loader.add_value('image_urls', base_image+'/'+color_code)
        return loader.load_item()


