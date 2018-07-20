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


if __name__ == '__main__':
    parse()