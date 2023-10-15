from enum import Enum

from coin_checko_api import CoinGeckoAPI
from typing import List, Dict
import json
import pandas as pd
from utils import write_json_file, print_progress


class CandleInterval(Enum):
    # Daily only available t - 3 months
    DAILY = 1
    # 1 day from current time = 5 minute interval data
    # 2 - 90 days of date range = hourly data
    # above 90 days of date range = daily data (00:00 UTC)
    AUTO = 2

    def url_query_params(self) -> str:
        match self:
            case CandleInterval.DAILY:
                return "&days=180&interval=daily"
            case CandleInterval.AUTO:
                return "&days=max"

    def folder_name(self) -> str:
        match self:
            case CandleInterval.DAILY:
                return "candles_daily"
            case CandleInterval.AUTO:
                return "candles_auto"


def download_candle_datas(
    ids: List[str],
    interval: CandleInterval,
    api: CoinGeckoAPI
):
    ids_cnt = len(ids)
    for idx, coingecko_id in enumerate(ids):
        print_progress("Downloading candles " + coingecko_id, idx, ids_cnt)
        data = download_candle_data(coingecko_id, interval, api)
        if data is not None:
            write_json_file(
                "data/" + interval.folder_name() + "/" + coingecko_id + ".json",
                data
            )


def download_candle_data(
    id: str,
    interval: CandleInterval,
    api: CoinGeckoAPI
) -> List[Dict[str, any]]:
    url = "https://api.coingecko.com/api/v3/coins/" + id + "/ohlc"
    url += "?vs_currency=usd&precision=full" + interval.url_query_params()
    response = api.fetch_content(url)
    return None if response is None else json.loads(response)


def candles_data_to_df(candles: List[List[int]]) -> pd.DataFrame:
    df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close'])
    for idx, candle in enumerate(candles):
        df.loc[idx] = candle
    df['timestamp'] = df.apply(lambda x: int(x['timestamp'] / 1000), axis=1)
    df = df.set_index('timestamp')
    return df