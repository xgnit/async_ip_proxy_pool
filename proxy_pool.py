
import json
from lxml import etree
import re
import random
import copy
import asyncio
import requests
import functools
import os
import aiohttp

class ProgressBar(object):

    @staticmethod
    def backward_print(str):
        sys.stdout.write("\033[33m\r{0}".format(str))
        sys.stdout.flush()
        sys.stdout.write('\033[4A')

    @staticmethod
    def build_progress_bar(all_ele, done_ele):
        progress = int(round(done_ele/all_ele, 1) * 100)
        progress_str = ''
        for i in range(progress):
            progress_str += '-'
        progress_str += '>'
        for i in range(100-progress):
            progress_str += '_'
        progress_str += '|'
        return progress_str
    @staticmethod
    def show_progress(str, all_ele, done_ele):
        string_to_print = ProgressBar.build_progress_bar(all_ele, done_ele)
        string_to_print = str + string_to_print
        ProgressBar.backward_print(string_to_print)

class Proxy(object):
    def __init__(self, update=True):
        self.source = 'https://free-proxy-list.net/'
        self.ip_element = "//div/table[@id='proxylisttable']/tbody/tr"

        self.ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        self.port_pattern = re.compile(r'^\d{1,5}$')
        self.proxy_no = self.good_proxy_no = self.bad_proxy_no = 0
        self.p_bar = None
        if update:
            self.update_proxy()

    @staticmethod
    def data_path():
        return os.path.abspath(os.path.join(os.path.dirname(__file__), 'proxy.json'))

    def read_proxy(self):
        try:
            with open(self.data_path(), "r") as f:
                return json.load(f)
        except Exception as e:
            print('Cannot find the previous local proxy file')
            return list()

    def write_proxy(self, content):
        try:
            with open(self.data_path(), 'w') as f:
                json.dump(content, f)
        except Exception as e:
            print('Failed to write the proxy json data to file: ' + str(e))

    @staticmethod
    def get_headers():
        user_agent = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)'
        ]
        return {'referer': r'https://www.google.com/', 'user-agent': user_agent[random.randint(0, 5)]}

    def get_proxy_from_internet(self):
        page = requests.get(self.source, headers=self.get_headers())
        html = etree.HTML(page.text)
        proxies = html.xpath(self.ip_element)
        proxy_list = []

        for i in proxies:
            res = i.xpath("./td[not(@*)]")
            ip = port = ''
            for i in res:
                if (self.ip_pattern.match(i.text)):
                    ip = i.text
                if (self.port_pattern.match(i.text)):
                    port = i.text
            if ip and port:
                proxy_list.append('http://{0}:{1}'.format(ip, port))
        return proxy_list

    def get_proxy(self):
        return self.read_proxy()

    def update_proxy(self):
        proxy_from_web = self.get_proxy_from_internet()
        proxy_from_local = self.read_proxy()
        proxy = copy.deepcopy(proxy_from_web) + copy.deepcopy(proxy_from_local)
        proxy = list(set(proxy))
        self.proxy_no = len(proxy)
        proxy = self.test_proxy_list(proxy)

        print('{} good proxies'.format(self.good_proxy_no))

        self.write_proxy(proxy)

    def print_info(self):
        print('All proxies being tested: {0}. Good proxies: {1}. Bad proxies: {2}'.format(self.proxy_no, self.good_proxy_no,
                                                                                          self.bad_proxy_no))
    def update(self):
        self.p_bar.update(self.good_proxy_no + self.bad_proxy_no)

    async def run(self, proxy):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url='https://www.google.com', proxy=proxy,
                                       headers=self.get_headers(), timeout=5) as resp:
                    self.good_proxy_no += 1
                    self.update()
                    ProgressBar.show_progress('Proxies tested: ', self.proxy_no, self.good_proxy_no)
                    return proxy
            except Exception as e:
                # print(str(e))
                self.bad_proxy_no += 1
                self.update()
                return None



    async def run_(self, proxy):
        loop = asyncio.get_event_loop()
        try:
            proxy_for_requests = {'https': proxy}
            response = await loop.run_in_executor(None, functools.partial(requests.get, url='https://www.google.com',
                                                                          headers=self.get_headers(), timeout=5,
                                                                          proxies=proxy_for_requests))
            self.good_proxy_no += 1
            self.update()
            # self.update(self.good_proxy_no + self.bad_proxy_no)
            # print("{} is good".format(proxy))
            return proxy
        except Exception as e:
            self.bad_proxy_no += 1
            self.update()
            # self.update(self.good_proxy_no + self.bad_proxy_no)
            # print("Cannot reach google: {}".format(str(e)))
            return None

    def test_proxy_list(self, proxy_list):
        print('Testing proxies...')
        # self.p_bar = progressbar.ProgressBar(max_value=self.proxy_no).start()
        tasks = [asyncio.ensure_future(self.run(proxy)) for proxy in proxy_list]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        res = [task.result() for task in tasks if task.result()]
        # self.p_bar.finish()
        return res



if __name__ == '__main__':
    # the default value fore update is True
    res = Proxy().get_proxy()






