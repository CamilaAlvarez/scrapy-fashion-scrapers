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
            item_json = dict(item)
            if os.path.exists(filename):
                with open(filename) as existing_json:
                    existing_item_json = json.load(existing_json)
                    item_json['categories'] = [item_json['categories'], existing_item_json['categories']]
            with open(filename, 'w') as output_json:
                json.dump(dict(item), output_json, indent=4)
        else:
            print("No output dir")
        return item
