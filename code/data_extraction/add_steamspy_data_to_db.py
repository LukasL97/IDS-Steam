import os
import re
import sys

from lxml import etree
from tinydb import TinyDB, Query
from tqdm import tqdm


def get_price_and_discount(html):
    price_with_discount_regex = '<strong>Price:</strong>\s*\$([0-9\.]+)\s*<font class=text-success><i class="fa fa-long-arrow-down"></i>([0-9]+)%'
    price_regex = '<strong>Price:</strong>\s*\$([0-9\.]+)'
    if '<strong>Free</strong>' in html:
        return 0.0, 0.0
    elif re.search(price_with_discount_regex, html):
        return (float(x) for x in re.search(price_with_discount_regex, html).groups())
    elif re.search(price_regex, html):
        return float(re.search(price_regex, html).groups()[0]), 0.0
    else:
        raise RuntimeError('Could not find any price indication')

def map_month_string_to_num(month):
    if month == 'Jan': return 1
    if month == 'Feb': return 2
    if month == 'Mar': return 3
    if month == 'Apr': return 4
    if month == 'May': return 5
    if month == 'Jun': return 6
    if month == 'Jul': return 7
    if month == 'Aug': return 8
    if month == 'Sep': return 9
    if month == 'Oct': return 10
    if month == 'Nov': return 11
    if month == 'Dec': return 12
    raise RuntimeError('Unexpected month %s' % month)

def get_release_data(html):
    release_date_regex = '<strong>Release date</strong>:\s*([A-Za-z]{3}) ([0-9]{1,2}), ([0-9]{4})'
    month, day, year = tuple(re.search(release_date_regex, html).groups())
    return int(day), map_month_string_to_num(month), int(year)

def get_steamspy_data(html):
    data = {}
    try:
        price, discount = get_price_and_discount(html)
        data['price'] = price
        data['discount'] = discount
    except RuntimeError:
        pass
    try:
        day, month, year = get_release_data(html)
        data['release_date'] = {
            'day': day,
            'month': month,
            'year': year
        }
    except:
        pass
    return data


if __name__ == '__main__':

    pages_path = sys.argv[1]
    files = os.listdir(pages_path)

    parser = etree.HTMLParser()

    db_path = sys.argv[2]
    db = TinyDB(db_path)

    game_documents = db.table('games').all()
    game_documents_dict = {game['app_id']: game for game in game_documents}

    for file in tqdm(files):
        with open(pages_path + file, encoding='utf8', mode='r') as page_file:
            page_code = page_file.read()

        app_id = file[:-5]

        game_documents_dict[app_id]['steamspy'] = get_steamspy_data(page_code)

    db.drop_table('games')
    db.table('games').insert_multiple(game_documents_dict.values())
