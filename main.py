import json
import os
import time
from dotenv import load_dotenv
from download_chart_data import download_chart_data
from download_markets import download_all_coins, download_markets, print_progress
from vpn_switcher.vpn_switcher import VPNSwitcher
import utils
import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Dict

load_dotenv()


def main():
    vpn_switcher = VPNSwitcher(
        os.environ.get("VPN_USER"),
        os.environ.get("VPN_PASS"),
    )
    vpn_switcher.next()

    print("Downloading coins")
    coins = download_all_coins()
    utils.write_json_file("data/coins.json", json.dumps(coins))

    print("Downloading markets")
    markets = download_markets(vpn_switcher)
    utils.write_json_file("data/markets.json", json.dumps(markets))

    # coin gecko does not return daily chart in nearest 3 months
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
            with open("data/chart/" + coingecko_id + "_usd_chart_data.json", 'w') as f:
                f.write(json.dumps(data))

    print("Failed indexes", failed_idxs)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
