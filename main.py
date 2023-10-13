import json
import os
import time
import requests
# import mysql.connector
from dotenv import load_dotenv

from download_chart_data import download_chart_data
from download_markets import download_all_coins, download_markets, print_progress
from vpn_switcher.vpn_switcher import VPNSwitcher
import utils
import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Dict

load_dotenv()

# db = mysql.connector.connect(
#     host=os.environ.get("DB_HOST"),
#     user=os.environ.get("DB_USER"),
#     passwd=os.environ.get("DB_PASS"),
#     database=os.environ.get("DB_NAME"),
# )
# cursor = db.cursor()


def main():
    # Download coins & markets
    import json
    from vpn_switcher.vpn_switcher import VPNSwitcher
    from download_markets import download_all_coins, download_markets

    vpn_switcher = VPNSwitcher(
        os.environ.get("VPN_USER"),
        os.environ.get("VPN_PASS"),
    )
    vpn_switcher.next()

    # print("Downloading coins")
    # coins = download_all_coins()
    # with open("tmp/coins.json", 'w') as f:
    #     f.write(json.dumps(coins))
    #
    # print("Downloading markets")
    # markets = download_markets(vpn_switcher)
    # with open("tmp/markets.json", 'w') as f:
    #     f.write(json.dumps(markets))

    markets = list()
    with open("tmp/markets.json", 'r') as f:
        markets = json.load(f)

    now = datetime.datetime.now() - relativedelta(months=3)
    ts = int(now.timestamp())
    failed_idxs = list()

    for idx in range(398, len(markets)):
        market = markets[idx]
        coingecko_id = market["id"]
        print_progress(coingecko_id, idx, len(markets))
        time.sleep(utils.REQ_INTERVAL)
        data = None
        try:
            data = download_chart_data(coingecko_id, 0, ts, vpn_switcher, 3)
        except:
            failed_idxs.append(idx)
            time.sleep(utils.REQ_INTERVAL_LONG)
            vpn_switcher.next()
            print("Failed indexes", failed_idxs)

        if data is not None:
            with open("tmp/" + coingecko_id + "_usd_chart_data.json", 'w') as f:
                f.write(json.dumps(data))

    print("Failed indexes", failed_idxs)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
