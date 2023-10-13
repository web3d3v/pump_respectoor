from utils import std_headers, REQ_INTERVAL
from vpn_switcher.vpn_switcher import VPNSwitcher
from typing import List, Dict
import requests
import time
import json


def download_chart_data(
    id: str,
    _from: int,
    to: int,
    vpn_switcher: VPNSwitcher,
    retry_cnt: int = 0
) -> List[Dict[str, any]]:
    url = "https://api.coingecko.com/api/v3/coins/"
    url += id + "/market_chart/range?vs_currency=usd"
    url += "&from={}&to={}&precision=18".format(_from, to)

    time.sleep(REQ_INTERVAL)
    response = requests.get(url, headers=std_headers(), stream=False)
    if response.status_code != 200:
        print(response.status_code)
        if retry_cnt == 0:
            return None
        vpn_switcher.next()
        time.sleep(2)
        return download_chart_data(id, _from, to, vpn_switcher, retry_cnt - 1)
    return json.loads(response.content)