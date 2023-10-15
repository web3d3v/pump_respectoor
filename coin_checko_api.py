import os
import time
import requests
from enum import Enum
from utils import std_headers
from vpn_switcher.vpn_switcher import VPNSwitcherInterface, VPNSwitcher
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class ExecPolicy(Enum):
    SLEEP = 1
    VPN = 2
    API_KEY = 3

    def request_sleep_interval(self) -> float:
        match self:
            case ExecPolicy.SLEEP:
                return 60.0 / 30.0
            case ExecPolicy.API_KEY:
                return 60.0 / 500.0
            case ExecPolicy.VPN:
                return 60.0 / 500.0


class CoinGeckoAPI:

    def __init__(self, exec_policy: ExecPolicy):
        self.exec_policy = exec_policy
        self.vpn_switcher: VPNSwitcherInterface | None = None
        self.api_key: str | None = None
        self.failed_requests: List[str] = list()

        if exec_policy == ExecPolicy.VPN:
            vpn_switcher = VPNSwitcher(
                os.environ.get("VPN_USER"),
                os.environ.get("VPN_PASS"),
            )
            vpn_switcher.next()

        if exec_policy == ExecPolicy.API_KEY:
            self.api_key = os.environ.get("COIN_GECKO_API")

    def fetch_content(self, url: str, retry_cnt: int = 3) -> bytes | None:
        response = self.fetch_response(url, retry_cnt)
        return None if response.status_code != 200 else response.content

    def fetch_response(self, url: str, retry_cnt: int = 3) -> requests.Response | None:
        time.sleep(self.exec_policy.request_sleep_interval())
        _url = url

        if self.exec_policy == ExecPolicy.API_KEY:
            _url = url + "&x_cg_pro_api_key=" + self.api_key

        response = requests.get(_url, headers=std_headers(), stream=False)

        if response.status_code == 429:

            match self.exec_policy:
                case ExecPolicy.SLEEP:
                    time.sleep(300)
                case ExecPolicy.API_KEY:
                    # Should never get to this state
                    time.sleep(300)
                case ExecPolicy.VPN:
                    self.vpn_switcher.next()

            if retry_cnt <= 0:
                self.failed_requests.append(url)
                print("Failed requests", self.failed_requests)
                return response

            self.fetch_response(url, retry_cnt - 1)

        return response
