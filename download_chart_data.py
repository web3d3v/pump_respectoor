from coin_checko_api import CoinGeckoAPI
from utils import print_progress, write_json_file
from typing import List, Dict
import json
import pandas as pd


def download_chart_datas(ids: List[str], _from: int, to: int, api: CoinGeckoAPI):
    ids_cnt = len(ids)
    for idx, coingecko_id in enumerate(ids):
        print_progress(coingecko_id, idx, ids_cnt)
        data = download_chart_data(coingecko_id, _from, to, api)
        if data is not None:
            write_json_file(
                "data/chart/" + coingecko_id + ".json",
                json.dumps(data)
            )


def download_chart_data(
    id: str,
    _from: int,
    to: int,
    api: CoinGeckoAPI,
) -> List[Dict[str, any]] | None:
    url = "https://api.coingecko.com/api/v3/coins/"
    url += id + "/market_chart/range?vs_currency=usd"
    url += "&from={}&to={}&precision=18".format(_from, to)

    response = api.fetch_content(url)
    return None if response is None else json.loads(response)


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