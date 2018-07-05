import scrapy
from fashion_scrapper.product_loader import ProductLoader
from fashion_scrapper.items import FashionScrapperItem


class OQVestirSpider(scrapy.Spider):
    name = 'oqvestir_spider'
    start_urls = ['https://www.oqvestir.com.br']

    def parse(self, response):
        main_categories = response.css('nav.header-menu div.container ul.nav-justified li')
        for i in range(len(main_categories)):
            if i < 3:
                continue
            main_category = main_categories[i]
            main_category_name = main_category.css('li a::text').extract_first()
            subcategories = main_category.css('li div.sub-menu div.row div.col-sm-2 ul.list-unstyled li')
            for subcategory in subcategories:
                if subcategory.xpath("@class").extract_first() == 'menu-subtitle':
                    continue
                subcategory_name = subcategory.css('a::text').extract_first()
                subcategory_url = subcategory.css('a::attr(href)').extract_first()
                yield response.follow(subcategory_url, callback=self.parse_category_page,
                                      meta={'categories': [main_category_name, subcategory_name]})

    def parse_category_page(self, response):
        categories = response.meta['categories']
        for subcategory in response.css('ul.even li a'):
            subcategory_name = subcategory.xpath('@title').extract_first()
            subcategory_url = subcategory.xpath('@href').extract_first()
            categories.append(subcategory_name)
            yield response.follow(subcategory_url, callback=self.parse_subcategory_page,
                                  meta={'categories': categories,
                                        'page_number': 0,
                                        'splash': {
                                            'args': {
                                                # set rendering arguments here
                                                'html': 1
                                            },
                                            'endpoint': 'render.html'
                                        }
                                        })

    def parse_subcategory_page(self, response):
        page_url = response.url
        page_number = response.meta['page_number']
        categories = response.meta['categories']
        if page_number == 0:
            total_page_number_selector = response.css('span.pagTotal::text').extract_first()
            if total_page_number_selector is None:
                print('total_page_number_selector is None')
                total_page_number = 1
            else:
                total_page_number = int(total_page_number_selector)

        else:
            total_page_number = response.meta['total_pages']
        metadata = {'page_number': page_number + 1,
                    'total_pages': total_page_number,
                    'categories': categories,
                    'splash': {
                        'args': {
                            # set rendering arguments here
                            'html': 1
                        },
                        'endpoint': 'render.html'
                    }}

        if page_number + 1 < total_page_number:
            new_url = page_url.replace('#{}'.format(page_number), '')
            new_url = '{}#{}'.format(new_url, page_number + 1)
            yield response.follow(new_url, callback=self.parse_subcategory_page, meta=metadata)

        for product in response.css('a.productImage::attr(href)').extract():
            yield response.follow(product, callback=self.parse_product,
                                  meta={'categories':categories,
                                        'splash': {
                                            'args': {
                                                # set rendering arguments here
                                                'html': 1
                                            },
                                            'endpoint': 'render.html'
                                        }})

    def parse_product(self, response):
        loader = ProductLoader(item=FashionScrapperItem(), response=response)
        loader.add_css('code', 'div.productReference::text')
        loader.add_css('name', 'hgroup.product-title h1 div::text')
        loader.add_css('details', 'hgroup.product-title h2 div::text')
        for description in response.css('div.productDescription ul li::text').extract():
            loader.add_value('description', description)
        for image in response.css('div.thumbnail ul.imagePlace ul li button img::attr(src)').extract():
            loader.add_value('image_urls', image)
        for category in response.meta['categories']:
            loader.add_value('categories', category)
        return loader.load_item()


