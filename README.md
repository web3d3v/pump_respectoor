# Pump Respectooor
<img src="pump_respectoor_v2.png"/>

Analyzing the frequency of pumps of coins listed on [Coin Gecko](https://www.coingecko.com/).

## NOTE: A lot of frequent changes. README lags behind, will be updated once it settles

## Usage 
Use `main.ipynb` to analyze the data

NOTE: Changes frequently, README might lag. 

`download_all_coins` downloads coin list from `/coins/list` endpoint and stores 
in `data/coins.json`.

`download_markets` downloads usd market for each coin from `coins/markets` 
endpoint. Stores in `data/markets.json`. Mainly used for rank and marketcap

`download_chart_data` downloads historical usd chart data (price, volume) from
`coins/${COIN_GECKO_ID}/market_chart/range` endpoint to 
`data/chart/${COIN_GECKO_ID}_usd_chart_data.json`. 10k plus files.

`dowload_candles` download historical candles `coins/${COIN_GECKO_ID}/ohlc`
stores to `data/candles/${COIN_GECKO_ID}.json`

Run `sudo python3 main.py` to download everything to `data/`. Will take about 
24h. then use main.ipynb to analyze data. Needs root privileges for VPN switching.


## Download data

Within a day or two data file would linked here. With exception of candle data
as it requires paid coin gecko account. You can download the data your self.

### VPN Config
Since Coin Gecko has 30 requests per minute limit for free API tear. Random VPN
profiles are used to scrape data faster. You can either create free
[protonmail](proton.me) account and download profiles at [OpenVpnIKEv2 profiles](https://account.proton.me/u/0/vpn/OpenVpnIKEv2)
. In theory should was with any openVPN profiles but untested. 

If you don't want to use VPN, replace `VPNSwitcher` with `SleepSwitcher`. This 
will increase scraping significantly. Instead of switching VPN it sleeps for 
5min. Currently, scraping takes about 24 hours with VPN. Without it would be 
days.

Highly recommended to run in the VM as VPN connection with change frequently

`.env` needs `VPN_USER=${YOUR_USER}` & `VPN_PASS=${YOUR_PASSdk}`. If downloading
candle data `COIN_GECKO_API=${YOUR_API_KEY}` as well. 




