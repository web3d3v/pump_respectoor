import requests
import time
import platform

REQ_INTERVAL = 2.1
REQ_INTERVAL_LONG = 5 * 60


def print_progress(prefix: str, curr: int, total: int):
    page_str = 'idx: {} / {}'.format(curr, total)
    prog_str = ', {:.1%}'.format(float(curr) / float(total))
    space = '       '
    # print('\r', prefix, page_str + prog_str + space, end='')
    print(prefix, page_str + prog_str + space)


def std_headers():
    headers = requests.utils.default_headers()
    default_agent = headers['User-Agent']
    headers.update({'User-Agent': default_agent + ' (' + platform.platform() + ')'})
    return headers


def get_ip():
    endpoint = 'https://ipinfo.io/json'
    response = requests.get(endpoint, verify=True)
    if response.status_code != 200:
        return 'Status:', response.status_code, 'Problem with the request. Exiting.'
        exit()
    data = response.json()
    return data['ip']


def sleep(seconds: int):
    i = seconds
    while i > 0:
        i = i - 1
        print("sleep", i, get_ip())
        time.sleep(1)