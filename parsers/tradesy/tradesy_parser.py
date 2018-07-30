from parsers.apparel_classes import classes_v1
from parsers.tradesy import *
import os
import json
import shutil
import click


@click.group()
def parse():
    pass


@parse.command()
@click.argument('base_json_folder')
@click.argument('output_base_folder')
def organize_products(base_json_folder, output_base_folder):
    """
    Organizes the products (organized as json files) scraped from tradesy.com
    It creates the folders inside an base output folder according to the apparel categories extracted from the
    website
    """
    products_json = os.listdir(base_json_folder)
    for product_json in products_json:
        product_json_path = os.path.join(base_json_folder, product_json)
        with open(product_json_path, encoding='utf-8') as product_file:
            product = json.load(product_file)
            categories = product['categories']
            category_folder = output_base_folder
            for category in categories:
                category_folder = os.path.join(category_folder, category)
            if not os.path.exists(category_folder):
                os.makedirs(category_folder)
            product_json_path_dst = os.path.join(category_folder, product_json)
            shutil.copyfile(src=product_json_path, dst=product_json_path_dst)


@parse.command()
@click.argument('tradesy_class_folder')
@click.argument('klass_needed')
@click.argument('output_folder')
def separate_in_definied_classes(tradesy_class_folder, klass_needed, output_folder):
    equivalent_categories = ['sneakers', 'pumps', 'wedges', 'sandals', 'flats', 'satchel', 'cross_body_bags', 'tote',
                             'clutch', 'backpack', 'weekend/travel_bag', 'scarf', 'sunglasses', 'belts', 'bracelet',
                             'ring', 'earrings', 'necklace', 'jacket', 'blazer', 'coat', 'sweatshirt_&_hoodie',
                             't-shirt', 'halter_top', 'cardigan', 'blouse', 'tank_top_&_camis', 'button_down_shirt',
                             'two_piece_swimsuit', 'one_piece_swimsuit', 'swimsuit_bottoms', 'swimsuit_top', 'pants',
                             'sweater_&_pullover', 'shorts', 'dress', 'skirt', 'jeans']
    if klass_needed in equivalent_categories:
        print('Category {} has a direct equivalent in tradesy'.format(klass_needed))
        return
    # walk until you find all json
    products_json = []
    for root, dirs, files in os.walk(tradesy_class_folder):
        for name in files:
            products_json.append(os.path.join(root, name))

    for product_json_path in products_json:
        product_json = open(product_json_path, encoding='utf-8')
        product = json.load(product_json)
        belongs_to_class = False
        if klass_needed == 'ankle_boots':
            belongs_to_class = is_ankle_boots(product)
        elif klass_needed == 'boots':
            belongs_to_class = is_boots(product)
        elif klass_needed == 'beanie':
            belongs_to_class = is_beanie(product)
        elif klass_needed == 'sun_hat':
            belongs_to_class = is_sun_hat(product)
        elif klass_needed == 'gloves':
            belongs_to_class = is_gloves(product)
        elif klass_needed == 'cap':
            belongs_to_class = is_cap(product)
        elif klass_needed == 'jumpsuit':
            belongs_to_class = is_jumpsuit(product)
        elif klass_needed == 'romper':
            belongs_to_class = is_romper(product)
        if belongs_to_class:
            shutil.copyfile(product_json_path, output_folder)



if __name__ == '__main__':
    parse()