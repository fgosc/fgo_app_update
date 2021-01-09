#!/usr/bin/python3
# アプリストアからFGOアプリの更新をチェックしてDiscordのwebhookにpostする
# au ゲーム版には未対応
import json
import argparse
import logging
from pathlib import Path
import configparser

import requests
from google_play_scraper import app
from bs4 import BeautifulSoup

inifile = "fgoappupdate.ini"

appstore_url = "https://apps.apple.com/jp/app/fate-grand-order/id1015521325"
basedir = Path(__file__).resolve().parent

logger = logging.getLogger(__name__)


def check_googlePlayStore(webhook_url, version_prev):
    result = app(
        'com.aniplex.fategrandorder',
        lang='ja',
        country='jp'
    )
    if result["version"] != version_prev:
        content = {
                        "username": "FGO アップデート",
                        "embeds": [{
                                "title": "FGO アプリアップデート (Google Play Store)",
                                "fields": [
                                    {
                                        "name": "バージョン",
                                        "value": result["version"]
                                    }, {
                                        "name": "更新内容",
                                        "value": result['recentChanges']
                                    }
                                ],
                                "color": 5620992
                                    }]
                        }
        requests.post(webhook_url,
                      json.dumps(content),
                      headers={'Content-Type': 'application/json'})
        return result["version"]
    return version_prev


def check_appStore(webhook_url, version_prev):
    """
    AppStoreのウェブサイトからスクレイピングで情報をゲットする
    レイアウトが変わった場合、変更が必要
    """
    html = requests.get(appstore_url)
    content = str(html.content).replace("<br />", "<br>")
    soup = BeautifulSoup(html.content, "html.parser")
    version = soup.select_one('p.whats-new__latest__version').get_text().replace("バージョン ", "")

    if version != version_prev:
        target_texts = soup.select('p[data-test-bidi]')
        for target_text in target_texts:
            if target_text.get_text().startswith("【"):
                for i in target_text.select("br"):
                    i.replace_with("\n")
                update_text = target_text.text
                break
        content = {
                        "username": "FGO アップデート",
                        "embeds": [{
                                "title": "FGO アプリアップデート (AppStore)",
                                "fields": [
                                    {
                                        "name": "バージョン",
                                        "value": version
                                    }, {
                                        "name": "更新内容",
                                        "value": update_text
                                    }
                                ],
                                "color": 5620992
                                    }]
                        }
        logger.debug(content)
        requests.post(webhook_url,
                      json.dumps(content),
                      headers={'Content-Type': 'application/json'})
        return version
    return version_prev


def main():
    config = configparser.ConfigParser()
    configfile = basedir / Path(inifile)
    if configfile.exists() is False:
        logger.critical("ファイル %s を作成してください", inifile)
        exit()
    config.read(configfile)
    section1 = 'discord'
    webhook_url = config.get(section1, 'webhook')
    logger.debug(webhook_url)

    section2 = 'appstore'
    iversion = config.get(section2, 'version')
    logger.debug(iversion)

    section3 = 'playstore'
    gversion = config.get(section3, 'version')
    logger.debug(gversion)

    try:
        iversion = check_appStore(webhook_url, iversion)
        gversion = check_googlePlayStore(webhook_url, gversion)
    except Exception as e:
        logger.error(e)

    config.set(section1, 'webhook', webhook_url)
    config.set(section2, 'version', iversion)
    config.set(section3, 'version', gversion)
    with open(basedir / Path(inifile), 'w') as f:
        config.write(f)


if __name__ == '__main__':
    # オプションの解析
    parser = argparse.ArgumentParser(
                description='Post FGO App update information to Discord'
                )
    # 3. parser.add_argumentで受け取る引数を追加していく
    parser.add_argument('-l', '--loglevel',
                        choices=('debug', 'info'), default='info')

    args = parser.parse_args()    # 引数を解析
    logging.basicConfig(
        level=logging.INFO,
        format='%(name)s <%(filename)s-L%(lineno)s> [%(levelname)s] %(message)s',
    )
    logger.setLevel(args.loglevel.upper())

    main()
