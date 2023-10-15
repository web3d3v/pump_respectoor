import json
from dotenv import load_dotenv
from coin_checko_api import CoinGeckoAPI, ExecPolicy
from download_candles import download_candle_datas, CandleInterval
from download_chart_data import download_chart_data, download_chart_datas, ChatInterval
from download_coin import download_coin_datas
from download_markets import download_all_coins, download_markets, print_progress
from utils import write_json_file, read_json_file
import datetime
from dateutil.relativedelta import relativedelta

load_dotenv()


def main():
    api = CoinGeckoAPI(ExecPolicy.API_KEY)

    print("Downloading coins")
    coins = download_all_coins(api)
    print(len(coins))
    write_json_file("data/coins.json", coins)

    print("Downloading markets")
    markets = download_markets(api)
    write_json_file("data/markets.json", markets)
    # markets = read_json_file("data/markets.json")
    coin_gecko_ids = list(map(lambda x: x["id"], markets))

    print("Downloading candle daily data")
    download_candle_datas(coin_gecko_ids, CandleInterval.DAILY, api)
    print("Failed requests:", len(api.failed_requests), api.failed_requests)

    print("Downloading chart data auto")
    download_chart_datas(coin_gecko_ids, ChatInterval.AUTO, api)
    print("Failed requests:", len(api.failed_requests), api.failed_requests)

    print("Downloading chart data")
    download_chart_datas(coin_gecko_ids, ChatInterval.DAILY, api)
    print("Failed requests:", len(api.failed_requests), api.failed_requests)

    print("Downloading coin data")
    download_coin_datas(coin_gecko_ids, api)
    print("Failed requests:", len(api.failed_requests), api.failed_requests)

    print("Downloading candle auto data")
    download_candle_datas(coin_gecko_ids, CandleInterval.AUTO, api)
    print("Failed requests:", len(api.failed_requests), api.failed_requests)

    print("Failed requests:", len(api.failed_requests))
    for url in api.failed_requests:
        print(url)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

