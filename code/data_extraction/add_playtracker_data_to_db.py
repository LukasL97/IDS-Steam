import os
import re
import sys

from lxml import etree
from tinydb import TinyDB, Query
from tqdm import tqdm

def is_steam_game_page(html_tree):
    return html_tree.xpath("//h4[@class='faded capitalize']/text() = 'on Steam'")

def get_popularity(html_tree):
    return int(html_tree.xpath("//div[contains(@class, 'hexagon')]/text()")[0])

def parse_estimated_players(estimation_string):
    regex_K = '^\~([0-9\.]+)K\*?$'
    regex_M = '^\~([0-9\.]+)M\*?$'
    if re.search(regex_K, estimation_string):
        return int(float(re.match(regex_K, estimation_string).groups()[0]) * 1000)
    elif re.search(regex_M, estimation_string):
        return int(float(re.match(regex_M, estimation_string).groups()[0]) * 1000000)
    else:
        raise RuntimeError('Estimation string "%s" can not be parsed' % estimation_string)

def get_estimated_players(html_tree):
    estimated_players_xpath = "//div[contains(@class, 'figure-total relative wow') and .//div[contains(@class, 'smaller-text faded')]/text() = 'estimated players']/div[contains(@class, 'superbold wider')]/text()[1]"
    return parse_estimated_players(html_tree.xpath(estimated_players_xpath)[0].strip())

def get_estimated_active_players(html_tree):
    estimated_active_players_xpath = "//div[contains(@class, 'figure-total relative wow') and .//div[contains(@class, 'smaller-text faded')]/text() = 'estimated active players']/div[contains(@class, 'superbold wider')]/text()[1]"
    return parse_estimated_players(html_tree.xpath(estimated_active_players_xpath)[0].strip())

def get_average_playtime(html_tree):
    average_playtime_xpath = "//div[contains(@class, 'figure-total relative wow') and .//div[contains(@class, 'smaller-text faded')]/text() = 'average total playtime']/div[contains(@class, 'superbold wider')]/text()[1]"
    playtime_regex = '^([0-9\.]+)h$'
    playtime = html_tree.xpath(average_playtime_xpath)[0]
    return float(re.match(playtime_regex, playtime).groups()[0])

def get_playtracker_data(html_tree):
    return {
        'popularity': get_popularity(html_tree),
        'estimated_players': get_estimated_players(html_tree),
        'estimated_active_players': get_estimated_active_players(html_tree),
        'average_playtime': get_average_playtime(html_tree)
    }

if __name__ == '__main__':

    pages_path = sys.argv[1]
    files = os.listdir(pages_path)

    parser = etree.HTMLParser()

    db_path = sys.argv[2]
    db = TinyDB(db_path)

    game_documents = []
    write_db_after = 1000

    Game = Query()

    game_documents = db.table('games').all()
    game_documents_dict = {game['app_id']: game for game in game_documents}

    for file in tqdm(files):
        with open(pages_path + file, encoding='utf8', mode='r') as page_file:
            page_code = page_file.read()
        html_tree = etree.fromstring(page_code, parser)

        app_id = file[:-5]

        if is_steam_game_page(html_tree):
            playtracker_data = {'playtracker': get_playtracker_data(html_tree)}
            game_documents_dict[app_id]['playtracker'] = get_playtracker_data(html_tree)
            print(game_documents_dict[app_id])
        else:
            pass

    db.drop_table('games')
    db.table('games').insert_multiple(game_documents_dict.values())
