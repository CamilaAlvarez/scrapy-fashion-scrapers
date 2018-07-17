import scrapy
from fashion_scrapper.product_loader import ProductLoader
from fashion_scrapper.items import FashionScrapperItem


class TheRealRealSpider(scrapy.Spider):
    name = 'the_real_real_spider'
    base_url = 'https://www.therealreal.com/'
    start_urls = [base_url]
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

    def start_requests(self):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers)

    def parse(self, response):
        for idx, category_section in enumerate(response.css('div.head-nav-menu.nav-menu.js-header-nav-menu')):
            if idx < 2:
                continue
            category_column = category_section.css('div.head-nav-menu__column '
                                                   '> div.head-nav-menu__inner-col.head-nav-menu__inner-col--grid')
            main_category_name = category_section.xpath('@data-menu').extract_first()
            for category in category_column:
                sub_category = category.css('div.head-nav-menu__item.head-nav-menu__item--title::text')\
                    .extract_first()
                for sub_sub_category in category_column.css('.head-nav-menu__item'):
                    sub_sub_category_url = sub_sub_category.xpath('@href').extract_first()
                    sub_sub_category_name = sub_sub_category.xpath('text()').extract_first()
                    sub_sub_category_class = sub_sub_category.xpath('@class').extract_first()
                    if sub_sub_category_name is None or len(sub_sub_category_name) <= 0:
                        continue
                    if 'head-nav-menu__item--title' in sub_sub_category_class:
                        sub_category = sub_sub_category_name
                        continue
                    elif 'head-nav-menu__item--strong' in sub_sub_category_class:
                        continue
                    yield response.follow('{}{}'.format(self.base_url, sub_sub_category_url[1:]),
                                          callback=self.parse_category_page,
                                          meta={'categories': [main_category_name, sub_category,
                                                               sub_sub_category_name],
                                                },
                                          headers=self.headers
                                          )

    def parse_category_page(self, response):
        url = response.url
        subclasses = response.css('form.js-taxon-filters > ul.plp-taxon-filters.taxon-filers__level-4 '
                                  'div.plp-bucket-list-filter.filter-body.js-filter-body > li '
                                  '> label.item')
        checked_checkbox = response.css('form.js-taxon-filters > ul.plp-taxon-filters.taxon-filers__level-4 '
                                        'div.plp-bucket-list-filter.filter-body.js-filter-body > li '
                                        '> label.item > input')
        print(checked_checkbox.extract())
        checked_checkbox = list(filter(lambda x: len(x.xpath('@checked')) > 0, checked_checkbox))
        print(checked_checkbox)
        if len(subclasses) > 0 or len(checked_checkbox) <= 0:
            # continue through the subclasses
            for subclass in subclasses:
                taxons_value = subclass.css('input::attr(value)').extract_first()
                subclass_name = subclass.css('span::text').extract_first()
                subclass_name = ' '.join(subclass_name.split(' ')[:-1])
                new_url = url
                if '?' in new_url:
                    new_url += ('&taxons%5B%5D=' + taxons_value)
                else:
                    new_url += ('?taxons%5B%5D=' + taxons_value)
                yield response.follow(new_url,
                                      callback=self.parse_category_page,
                                      meta={'categories': response.meta['categories'] + [subclass_name]})

        else:
            # download products
            #current_page_str = response.css('a.pagination__number.js-pagination__number'
            #                                '.pagination__number--highlighted::text').extract_first()
            #total_pages_str = response.css('a.pagination__number.js-pagination__number'
            #                               '.plp-pagination__number--prefix').extract()[-1]
            #current_page = int(current_page_str)
            #total_pages = int(total_pages_str)
            #if current_page == 1:
            #    url_parts = response.url.split('?')
            #    next_page_url = url_parts[0] + '?page=2' + '&' + url_parts[1]
            #elif current_page < total_pages:
            #    url_parts =  response.url.split('?page=')
            #    second_url_part = '&'.join(url_parts[1].split('&')[1:])
            #    next_page_url = url_parts[0] + '?page=' + str(current_page + 1) + '&' + second_url_part
            #else:
            #    return
            #yield response.follow(next_page_url, callback=self.parse_category_page, meta=response.meta)
            #products = response.css('div.product-card-wrapper.js-product-card-wrapper > a')
            #for product in products:
            #    product_url = product.xpath('@href').extract_first()
            #    product_url = '{}{}'.format(self.base_url, product_url)
            #    yield response.follow(product_url, callback=self.parse_product,
            #                          meta=response.meta)
            pass


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


