from utils import std_headers, REQ_INTERVAL
from vpn_switcher.vpn_switcher import VPNSwitcher
from typing import List, Dict
import requests
import time
import json
import pandas as pd


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


def chart_data_to_df(chart_data: List[Dict[str, any]], ) -> pd.DataFrame:
    tss = map(lambda x: int(x[0] / 1000), chart_data["prices"])
    vals = map(lambda x: x[1], chart_data["prices"])
    df = pd.DataFrame(data={'timestamp': tss, "price": vals})
    df = df.set_index('timestamp')

    tss = map(lambda x: int(x[0] / 1000), chart_data["market_caps"])
    vals = map(lambda x: x[1], chart_data["market_caps"])
    df_mcap = pd.DataFrame(data={'timestamp': tss, "market_cap": vals})
    df_mcap = df_mcap.set_index('timestamp')
    df = pd.concat([df, df_mcap], axis=1)

    tss = map(lambda x: int(x[0] / 1000), chart_data["total_volumes"])
    vals = map(lambda x: x[1], chart_data["total_volumes"])
    df_vol = pd.DataFrame(data={'timestamp': tss, "total_volume": vals})
    df_vol = df_vol.set_index('timestamp')
    df = pd.concat([df, df_vol], axis=1)

    return df