import sys
import urllib.parse

import requests
from lxml import etree
from tinydb import TinyDB
from tqdm import tqdm


def generate_search_term(game_title):
    return urllib.parse.quote(game_title)

def get_search_result_page(search_term, parser):
    response = requests.get('https://playtracker.net/search/?q=%s' % search_term)
    if not response.status_code == 200:
        print('Unexpected status %d' % response.status_code)
    html = response.text
    return etree.fromstring(html, parser)

def extract_steam_game_page_url(search_result_page, game_title):
    search_results = search_result_page.xpath("/html/body/main/div/div/div/div[contains(@class, 'search-result')]/a")
    try:
        search_results = [s for s in search_results if s.xpath("//div[@class='full']/text() = '%s'" % game_title)]
    except etree.XPathEvalError: # that's so dumb
        search_results = [s for s in search_results if s.xpath('//div[@class="full"]/text() = "%s"' % game_title)]
    search_results = [s for s in search_results if s.xpath("./div/div/*[name()='svg']/@data-icon = 'steam-symbol'")]
    if len(search_results) == 1:
        return search_results[0].xpath('./@href')[0]
    else:
        raise RuntimeError('Unexpected amount of search results for %s: %d' % (game_title, len(search_results)))

def dump_steam_game_page(url, app_id, path):
    response = requests.get(url)
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
        search_result_page = get_search_result_page(generate_search_term(game['name']), parser)
        try:
            steam_game_page_url = extract_steam_game_page_url(search_result_page, game['name'])
            dump_steam_game_page(steam_game_page_url, game['app_id'], dump_path)
        except RuntimeError:
            pass
        with open(dump_path + 'covered_app_ids.txt', mode='a+') as covered_app_ids_file:
            covered_app_ids_file.write(game['app_id'] + '\n')
