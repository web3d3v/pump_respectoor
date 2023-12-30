from download_candles import daily_candle_data_to_df
from download_coin import get_address_and_decimals
from utils import year_month_day_str
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from typing import List, Dict
import pandas as pd


def daily_candle_pumps_info_unwrap(args) -> pd.DataFrame:
    return daily_candle_pumps_info(*args)


def daily_candle_pumps_info(
    candle_data: List[List[any]], pump_ratio: float, min_volume: float,
    chart_df: pd.DataFrame, shift_volume: bool = False
) -> pd.DataFrame:
    df = daily_candle_data_to_df(candle_data)
    if shift_volume:
        chart_df = chart_df.shift(1, axis=0)
    df = df.join(chart_df)
    df = df.drop(['price', 'market_cap'], axis=1)
    df['Ymd'] = list(map(lambda x: year_month_day_str(x), df.index))
    df['pump'] = (df['high'] >= df['open'] * pump_ratio) & (df['volume'] > min_volume)
    return df.loc[df['pump'] == True]


def candle_pumps(
    daily_candles: Dict[str, List[List[any]]],
    df_charts: Dict[str, pd.DataFrame],
    ratio: float,
    min_vol: int,
) -> Dict[str, pd.DataFrame]:
    pumps: Dict[str, pd.DataFrame] = dict()
    keys, vals, dfs = (list(), list(), list())

    for idx, key in enumerate(daily_candles):
        if key in df_charts:
            keys.append(key)
            vals.append((daily_candles[key], ratio, min_vol, df_charts[key]))

    with Pool(processes=cpu_count()) as p:
        for df in tqdm(p.imap(daily_candle_pumps_info_unwrap, vals), total=len(vals)):
            dfs.append(df)
            p.close()
            p.join()

    for idx, key in enumerate(keys):
        if not dfs[idx].empty:
            pumps[key] = dfs[idx]
    return pumps


def filter_eth_erc20(dictionary: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    filtered = dict()

    for key, df in dictionary.items():
        address, decimals = get_address_and_decimals(key)
        if address is not None and decimals is not None:
            filtered[key] = df

    return filtered
