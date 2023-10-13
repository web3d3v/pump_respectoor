from utils import std_headers
from typing import List, Dict
import requests
import time
import json
import os
import pandas as pd

CANDLE_REQ_INTERVAL = 1.0 / 495.0
API_KEY = os.environ.get("COIN_GECKO_API")


def download_candle_data(
    id: str,
    retry_cnt: int = 0
) -> List[Dict[str, any]]:
    url = "https://api.coingecko.com/api/v3/coins/" + id + "/ohlc"
    url += "?vs_currency=usd&days=max&precision=18&interval=daily"

    time.sleep(CANDLE_REQ_INTERVAL)
    response = requests.get(url, headers=std_headers(), stream=False)
    if response.status_code != 200:
        print(response.status_code)
        if retry_cnt == 0:
            return None
        time.sleep(2)
        return download_candle_data(id, retry_cnt - 1)
    return json.loads(response.content)


def candles_data_to_df(candles: List[List[int]]) -> pd.DataFrame:
    df = pd.DataFrame(columns=['timestamp','open','high','low', 'close'])
    for idx, candle in enumerate(candles):
        df.loc[idx] = candle
    df['timestamp'] = df.apply(lambda x: int(x['timestamp'] / 1000), axis=1)
    df = df.set_index('timestamp')
    return df