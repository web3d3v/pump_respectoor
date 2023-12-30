from web3_utils import format_decimals, get_block_near
from utils import read_str_file, year_month_day_str, ranges_list
from web3 import Web3, AsyncWeb3
import web3
from multiprocessing import Pool, cpu_count
import datetime
import time
from tqdm import tqdm
from download_candles import daily_candle_data_to_df
from download_chart_data import chart_data_to_df
from utils import print_progress, year_month_str, year_month_day_str
from utils import read_json_file, write_json_file, read_json_file_or_empty_list
from utils import large_num_short_format
from dotenv import load_dotenv
from typing import  List, Dict
from utils import print_progress
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
import web3
import math
from download_coin import get_address_and_decimals
from utils import read_json_file, write_json_file, read_json_file_or_empty_list
from utils import large_num_short_format
from dotenv import load_dotenv
from typing import  List, Dict
from utils import print_progress
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import  math
import os
import pickle
import web3

load_dotenv()


provider_url = 'http://127.0.0.1:8545'


def new_provider(url: str, timeout: int = 120) -> web3.Web3:
    return Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': timeout}))


provider = new_provider(provider_url)


def block_num_for_timestamp(timestamp: int, provider: web3.Web3) -> int:
    return get_block_near(timestamp, provider)


def log_to_list(log: any, decimals: int) -> List[any]:
    val = log.args['value']
    return [
        provider.to_hex(log['transactionHash']),  # tx_hash
        log['transactionIndex'],  # tx_idx
        int(log['blockNumber']),  # blk_num
        timestamp,  # timestamp
        log.args['from'],  # frm
        log.args['to'],  # to
        val,  # val
        format_decimals(val, str(decimals)),  # dec
    ]


def get_logs_df_wrk_unwrap(args) -> pd.DataFrame:
    return get_logs_df_wrk(*args)


def get_logs_df_wrk(
        addr: str, abi: any, dec: int, provider_url: str, frm: int, to: int, retry: bool = True
) -> pd.DataFrame:
    df = pd.DataFrame(columns=[
        'tx_hash', 'tx_idx', 'blk_num', 'timestamp', 'frm', 'to', 'val', 'dec'
    ])
    addr = Web3.to_checksum_address(addr)
    provider = new_provider(provider_url)
    contract = provider.eth.contract(address=addr, abi=abi)
    logs = list()
    try:
        logs = contract.events.Transfer().get_logs(fromBlock=frm, toBlock=to)
        for log in logs:
            df.loc[len(df.index)] = log_to_list(log, dec)
    except Exception as err:
        if retry:
            print('({}, {}) {} will retry'.format(frm, to, err))
            time.sleep(1)
            return get_logs_df_wrk(addr, abi, dec, provider_url, frm, to, False)
        else:
            print('({}, {}) {} ERR !!!'.format(frm, to, err))
    return df


# tx_hash block_num timestamp frm to val dec #Ymd
def get_logs_df(
        coin_id: str,
        pump_timestamp: int,
        days: int,
        provider_url: str
) -> pd.DataFrame:
    print('get_logs_df', coin_id)
    addr, dec = get_address_and_decimals(coin_id)
    if addr is None or dec is None:
        return None

    provider = new_provider(provider_url)
    pump_block_num = block_num_for_timestamp(pump_timestamp, provider)
    st_block = pump_block_num - days * 24 * 60 * 5
    ranges = ranges_list(st_block, pump_block_num + (5 * 24 * 60 * 5), 200)
    print('({}, {})'.format(st_block, ranges[len(ranges) - 1][1]))
    abi = read_str_file('IERC20.json')
    df = pd.DataFrame(columns=[
        'tx_hash', 'tx_idx', 'blk_num', 'timestamp', 'frm', 'to', 'val', 'dec'
    ])
    dfs = []
    with Pool(processes=cpu_count()) as p:
        vals = map(lambda x: (addr, abi, dec, provider_url, x[0], x[1]), ranges)
        vals = list(vals)
        # dfs = p.map(get_logs_df_wrk_unwrap, vals)
        for res in tqdm(p.imap_unordered(get_logs_df_wrk_unwrap, vals), total=len(vals)):
            dfs.append(res)
        p.close()
        p.join()
    for batch_df in dfs:
        df = pd.concat([df, batch_df], ignore_index=True)
    return df


def log_to_tx_wrk_unwrap(args) -> any:
    return log_to_tx_wrk(*args)


def log_to_tx_wrk(
        idx: int, tx_idx: int, blk_num: int, provider_url: str, retry: bool = True
) -> any:
    provider = new_provider(provider_url)
    tx = provider.eth.get_transaction_by_block(int(blk_num), int(tx_idx))
    input = provider.to_hex(tx.input)
    method_bytes = input[:10]
    if method_bytes == '0xa9059cbb':
        return idx, 'transfer', "0x" + input[34:74]
    else:
        return idx, 'unknown', None


def flatten_logs_to_tx(coin_id: str, df: pd.DataFrame, provider_url: str) -> pd.DataFrame:
    print('flatten_logs_to_tx')
    df = df.copy()
    df.drop_duplicates('tx_hash', inplace=True)
    df.insert(df.shape[1], 'method', np.arange(0, df.shape[0]))

    vals = list()
    for i in range(len(df.index)):
        idx = df.index[i]
        tx_idx = int(df.loc[idx, 'tx_idx'])
        blk_num = int(df.loc[idx, 'blk_num'])
        vals.append((idx, tx_idx, blk_num, provider_url))

    results = list()
    with Pool(processes=cpu_count()) as p:
        for res in tqdm(p.imap_unordered(log_to_tx_wrk_unwrap, vals), total=len(vals)):
            results.append(res)
        p.close()
        p.join()

    for idx, res in enumerate(results):
        df.loc[res[0], 'method'] = res[1]
        if res[2] is not None:
            df.loc[res[0], 'to'] = res[2]

    return df


def timestamp_for_block_num_wrk_unwrap(args):
    return timestamp_for_block_num_wrk(*args)


def timestamp_for_block_num_wrk(block_num: int, provider_url: str) -> int:
    return new_provider(provider_url).eth.get_block(block_num)['timestamp']


def timestamp_for_block_num(df: pd.DataFrame, provider_url: str) -> pd.DataFrame:
    print('timestamp_for_block_num')
    df = df.copy()
    results = list()
    with Pool(processes=cpu_count()) as p:
        args = list(map(lambda x: (x, provider_url), df['blk_num']))
        for res in tqdm(p.imap(timestamp_for_block_num_wrk_unwrap, args), total=len(args)):
            results.append(res)
        p.close()
        p.join()

    df['timestamp'] = results
    df['Ymd'] = list(map(lambda x: year_month_day_str(x), df['timestamp']))
    return df


# Ymd tx_cnt, tx_val_total, eoa_tx_cnt, eoa_val_total
def grouped_by_day(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    grouped = df.groupby('Ymd')
    res_df = pd.DataFrame(columns=['Ymd', 'txs_cnt', 'txs_val', 'eoa_txs_cnt', 'eoa_txs_val'])
    print("groups", len(grouped))
    for key, group in grouped:
        eoa_txs = group[group['method'] == 'transfer']
        eoa_txs_cnt = len(eoa_txs)
        eoa_txs_val = ceil(eoa_txs['dec'].sum())
        row = [key, len(group), ceil(group['dec'].sum()), eoa_txs_cnt, eoa_txs_val]
        res_df.loc[len(res_df.index)] = row

    res_df['tx_cnt_pct'] = res_df['eoa_txs_cnt'] / res_df['txs_cnt']
    res_df['tx_val_pct'] = res_df['eoa_txs_val'] / res_df['txs_val']
    res_df['high_swap'] = res_df['tx_val_pct'] < 0.5  # res_df['eoa_txs_val'] / res_df['txs_val']
    res_df = res_df.round({'tx_cnt_pct': 4, 'tx_val_pct': 4})
    return res_df


from download_chart_data import ChartInterval
from download_chart_data import load_chart_by_interval, chart_data_to_df
from download_candles import load_candles_by_interval, CandleInterval


def main():
    # Load charts and candles
    daily_candles = load_candles_by_interval(CandleInterval.DAILY)
    charts = load_chart_by_interval(ChartInterval.FULL)

    print("Hello world")
    pd.set_option('display.width', 256)
    pd.set_option('display.max_colwidth', 24)

    start = time.time()
    df = eth_df_candles_pumps[coin_id]
    print(coin_id, year_month_day_str(timestamp))
    df_logs = get_logs_df(coin_id, timestamp, 90, provider_url)
    print("logs secs", time.time() - start, df_logs.shape)

    df_tx = df_logs.copy()
    df_tx = flatten_logs_to_tx(coin_id, df_tx, provider_url)
    print(df_tx.shape)
    # tx_hash block_num timestamp frm to val dec Ymd
    df_tx = timestamp_for_block_num(df_tx, provider_url)
    print(df_tx.shape)

    # Ymd tx_cnt, tx_val_total, eoa_tx_cnt, eoa_val_total
    res_df = grouped_by_day(df_tx)
    print(res_df.to_string())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
