import json
from dotenv import load_dotenv
from coin_checko_api import CoinGeckoAPI, ExecPolicy
from download_candles import download_candle_datas
from download_chart_data import download_chart_data, download_chart_datas
from download_markets import download_all_coins, download_markets, print_progress
import utils
import datetime
from dateutil.relativedelta import relativedelta

load_dotenv()


def main():
    api = CoinGeckoAPI(ExecPolicy.SLEEP)

    print("Downloading coins")
    coins = download_all_coins(api)
    utils.write_json_file("data/coins.json", json.dumps(coins))

    print("Downloading markets")
    markets = download_markets(api)
    utils.write_json_file("data/markets.json", json.dumps(markets))
    coin_gecko_ids = list(map(lambda x: x["id"], markets))

    print("Downloading candle data")
    download_candle_datas(coin_gecko_ids, api)
    print("Failed requests:", len(api.failed_requests), api.failed_requests)

    print("Downloading chart data")
    # coin gecko does not return daily chart in nearest 3 months
    now = datetime.datetime.now() # - relativedelta(months=3)
    ts = int(now.timestamp())
    download_chart_datas(coin_gecko_ids, 0, ts, api)
    print("Failed requests:", len(api.failed_requests), api.failed_requests)

    print("Failed requests:", len(api.failed_requests))
    for url in api.failed_requests:
        print(url)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

