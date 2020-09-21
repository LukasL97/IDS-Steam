
import sys
import os
import requests
from tqdm import tqdm

def get_apps():
    response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
    return response.json()['applist']['apps']

def dump_steamstore_page(app_id, path):
    response = requests.get('https://store.steampowered.com/app/%s' % app_id)
    if not response.status_code == 200:
        print('Unexpected status %d' % response.status_code)
    html = response.text
    with open('%s%s.html' % (path, app_id), encoding='utf8', mode='w+') as html_file:
        html_file.write(html)

if __name__ == '__main__':

    path = sys.argv[1]
    downloaded_app_ids = [file_name[:-5] for file_name in os.listdir(path)]

    apps = [app for app in get_apps() if not str(app['appid']) in downloaded_app_ids]
    for app in tqdm(apps):
        try:
            dump_steamstore_page(app['appid'], path)
        except:
            pass
