

def _get_product_description(product_json):
    if 'description' not in product_json:
        return ''
    return product_json['description'].lower().strip()


def _get_product_name(product_json):
    if 'name' not in product_json:
        return ''
    return product_json['name'].lower().strip()


def _is_of_class_generic(product_json, klass):
    prod_name = _get_product_name(product_json)
    return klass in prod_name


def _is_of_class_generic_by_description(product_json, klass):
    prod_description = _get_product_description(product_json)
    return klass in prod_description


def is_boots(product_json):
    prod_description = _get_product_description(product_json)
    return 'boots' in prod_description and 'ankle boots' not in prod_description and 'bootie' not in prod_description


def is_ankle_boots(product_json):
    prod_description = _get_product_description(product_json)
    return ('booties' in prod_description or 'ankle boots'  in prod_description) and 'boots' not in prod_description


def is_gloves(product_json):
    return _is_of_class_generic(product_json, 'gloves')


def is_beanie(product_json):
    prod_name = _get_product_name(product_json)
    prod_description = _get_product_description(product_json)
    return 'beanie' in prod_description or 'beanie' in prod_name


def is_cap(product_json):
    prod_name = _get_product_name(product_json)
    prod_description = _get_product_description(product_json)
    return 'cap' in prod_description or 'cap' in prod_name or 'baseball' in prod_description or 'baseball' in prod_name


def is_jumpsuit(product_json):
    return _is_of_class_generic_by_description(product_json, 'jumpsuit')


def is_romper(product_json):
    return _is_of_class_generic_by_description(product_json, 'romper')


def is_sun_hat(product_json):
    prod_name = _get_product_name(product_json)
    return 'fedora' in prod_name or 'brimmed' in prod_name or 'boater' in prod_name or 'panama' in prod_name or\
           ('hat' in prod_name and ('straw' in prod_name or 'floppy' in prod_name))
