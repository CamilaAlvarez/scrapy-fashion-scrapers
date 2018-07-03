# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os


class FashionScrapperPipeline(object):
    output_key = 'output_dir'

    def process_item(self, item, spider):
        output_dir = getattr(spider, self.output_key, False)
        if output_dir:
            product_code = item['code']
            filename = os.path.join(output_dir,'{}.json'.format(product_code))
            with open(filename, 'w') as output_json:
                json.dump(dict(item), output_json, indent=4)
        else:
            print("No output dir")
        return item
