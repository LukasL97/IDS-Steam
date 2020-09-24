import sys
import time

import requests
from lxml import etree
from tinydb import TinyDB
from tqdm import tqdm

def dump_steamspy_page(app_id, path):
    response = requests.get('https://steamspy.com/app/%s' % app_id)
    if not response.status_code == 200:
        print('Unexpected status %d' % response.status_code)
    html = response.text
    with open('%s%s.html' % (path, app_id), encoding='utf8', mode='w+') as html_file:
        html_file.write(html)

if __name__ == '__main__':

    dump_path = sys.argv[1]
    db_path = sys.argv[2]

    db = TinyDB(db_path)

    parser = etree.HTMLParser()

    with open(dump_path + 'covered_app_ids.txt', mode='r') as covered_app_ids_file:
        covered_app_ids = set([id.strip() for id in covered_app_ids_file.read().split('\n') if not id.strip() == ''])

    for game in tqdm([game for game in db.table('games').all() if not game['app_id'] in covered_app_ids]):
        dump_steamspy_page(game['app_id'], dump_path)
        with open(dump_path + 'covered_app_ids.txt', mode='a+') as covered_app_ids_file:
            covered_app_ids_file.write(game['app_id'] + '\n')
        time.sleep(0.1)