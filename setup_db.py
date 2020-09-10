
import os
import re
import sys

from lxml import etree
from tinydb import TinyDB
from tqdm import tqdm


def is_game_page(html_tree):
    is_in_all_games_category_xpath = "boolean(/html/body/div[contains(@class, 'responsive_page')]/div[@class='responsive_page_content']/div[@class='responsive_page_template_content']/div[contains(@class, 'game_page')]/div[@class='page_content_ctn']/div[contains(@class, 'game_title')]/div[@class='breadcrumbs']/div/a[1]/text() = 'All Games')"
    return html_tree.xpath(is_in_all_games_category_xpath)

def extract_game_tags(html_tree):
    game_tags_xpath = "/html/body/div[contains(@class, 'responsive_page')]/div[@class='responsive_page_content']/div[@class='responsive_page_template_content']/div[contains(@class, 'game_page')]/div[@class='page_content_ctn']/div[@class='block']//div[contains(@class, 'popular_tags')]/a/text()"
    return [tag.strip() for tag in html_tree.xpath(game_tags_xpath)]

def clean_int_string(int_string):
    return int(int_string.replace(',', ''))

def extract_reviews(html_tree):
    reviews_xpath = "/html/body/div[contains(@class, 'responsive_page')]/div[@class='responsive_page_content']/div[@class='responsive_page_template_content']/div[contains(@class, 'game_page')]/div[@class='page_content_ctn']/div[@class='block']//div[@class='user_reviews']/div[@class='user_reviews_summary_row']/@data-tooltip-html"
    reviews_strings = html_tree.xpath(reviews_xpath)
    recent_reviews_regex = '([0-9]+)% of the ([0-9,]+) user reviews in the last 30 days are positive.'
    overall_reviews_regex = '([0-9]+)% of the ([0-9,]+) user reviews for this game are positive.'
    reviews = {}
    for reviews_string in reviews_strings:
        if re.search(recent_reviews_regex, reviews_string):
            recent_reviews_rating, recent_reviews_count = tuple([clean_int_string(num) for num in re.match(recent_reviews_regex, reviews_string).groups()])
            reviews['recent'] = {'rating': recent_reviews_rating, 'count': recent_reviews_count}
        elif re.search(overall_reviews_regex, reviews_string):
            overall_reviews_rating, overall_reviews_count = tuple([clean_int_string(num) for num in re.match(overall_reviews_regex, reviews_string).groups()])
            reviews['overall'] = {'rating': overall_reviews_rating, 'count': overall_reviews_count}
        elif re.search('Need more user reviews to generate a score', reviews_string) or re.search('No user reviews', reviews_string):
            reviews['overall'] = 'need_more_reviews'
        else:
            raise RuntimeError('Unexpected reviews string: %s' % reviews_string)
    return reviews

def create_game_document(app_id, html_tree):
    return {
        'app_id': app_id,
        'tags': extract_game_tags(html_tree),
        'reviews': extract_reviews(html_tree)
    }


if __name__ == '__main__':

    pages_path = sys.argv[1]
    files = os.listdir(pages_path)

    parser = etree.HTMLParser()

    db_path = sys.argv[2]
    db = TinyDB(db_path)
    db.drop_table('games')
    db.table('games')

    game_documents = []

    for file in tqdm(files):
        with open(pages_path + file, encoding='utf8', mode='r') as page_file:
            page_code = page_file.read()

        html_tree = etree.fromstring(page_code, parser)

        if is_game_page(html_tree):
            game_document = create_game_document(file[:-5], html_tree)
            game_documents.append(game_document)

    db.table('games').insert_multiple(game_documents)
