from coin_checko_api import CoinGeckoAPI
from typing import List, Dict
import json
import pandas as pd
from utils import write_json_file, print_progress


def download_candle_datas(ids: List[str], api: CoinGeckoAPI):
    ids_cnt = len(ids)
    for idx, coingecko_id in enumerate(ids):
        print_progress(coingecko_id, idx, ids_cnt)
        data = download_candle_data(coingecko_id, api)
        if data is not None:
            write_json_file(
                "data/candles/" + coingecko_id + ".json",
                json.dumps(data)
            )


def download_candle_data(
    id: str,
    api: CoinGeckoAPI
) -> List[Dict[str, any]]:
    url = "https://api.coingecko.com/api/v3/coins/" + id + "/ohlc"
    url += "?vs_currency=usd&days=max&precision=18&interval=daily"
    response = api.fetch_content(url)
    return None if response is None else json.loads(response)


def candles_data_to_df(candles: List[List[int]]) -> pd.DataFrame:
    df = pd.DataFrame(columns=['timestamp','open','high','low', 'close'])
    for idx, candle in enumerate(candles):
        df.loc[idx] = candle
    df['timestamp'] = df.apply(lambda x: int(x['timestamp'] / 1000), axis=1)
    df = df.set_index('timestamp')
    return df