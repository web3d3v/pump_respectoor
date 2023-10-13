import requests
import time
import urllib
import json
from typing import List, Dict
from utils import std_headers, print_progress, REQ_INTERVAL
from vpn_switcher.vpn_switcher import VPNSwitcherInterface


def download_all_coins() -> List[Dict[str, any]]:
    url = 'https://api.coingecko.com/api/v3/coins/list?include_platform=true'
    response = urllib.request.urlopen(url)
    return json.loads(response.read())


def markets_url(page: int) -> str:
    url = "https://api.coingecko.com/api/v3/coins/markets"
    url += "?vs_currency=usd&order=market_cap_desc&per_page=250&page=" + str(page)
    url += "&sparkline=false&price_change_percentage=24h"
    return url


def download_markets(vpn_switcher: VPNSwitcherInterface) -> List[Dict[str, any]]:
    page_total = int(len(download_all_coins()) / 250)
    page = 1
    result_markets = list()
    while True:
        url = markets_url(page)
        response = requests.get(url, headers=std_headers(), stream=False)
        if response.status_code == 200:
            page_markets = json.loads(response.content)
            result_markets += page_markets
            print_progress('Download markets', page, page_total)
            time.sleep(REQ_INTERVAL)
            if len(page_markets) == 0:
                print_progress('Completed', page, page_total)
                break
            page += 1
        elif response.status_code == 429:
            print_progress('Switching VPN', page, page_total)
            vpn_switcher.next()
        else:
            msg = 'Unexpected:' + str(response.status_code)
            print_progress(msg, page, page_total)
            break
    return result_markets
