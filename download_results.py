import time
import json
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from functions import start_chrome
from multiprocessing import current_process
from vars import result_links


def download_html(chrome, base_link, reg):
    # chrome
    try:
        i = 0
        while True:
            if i % 10 == 0:
                chrome.get(f"{base_link}{reg}")
            time.sleep(.1)
            source = chrome.page_source
            i += 1
            if "New Official Website of Aryabhatta Knowledge University" in source:
                break
        return chrome.page_source
    except Exception as e:
        return None


def download_html_bs(base_link, reg):
    # Request
    try:
        i = 0
        while True:
            req = urlopen(f"{base_link}{reg}")
            if i % 10 == 0:
                time.sleep(.1)
            i += 1
            if req.code == 200:
                html = req.read()
                break
        return html
    except:
        return None


def download_and_save_results(base_link, REGS, OUT_DIR, dump_json=False):
    process_name = current_process().name.lower()
    chrome = start_chrome()
    json_data = dict()
    for reg in REGS:
        html = download_html(chrome, base_link, reg)
        if html:
            try:
                with open(os.path.join(OUT_DIR, f'{reg}.html'), 'w', encoding='utf-8') as f:
                    f.write(html)
                if dump_json:
                    data = to_json(html)
                    json_data[reg] = data
                    with open(os.path.join(OUT_DIR, f'_{process_name}_data.json'), 'w') as f:
                        json.dump(json_data, f, indent=2)
            except:
                # invalid reg
                continue
    chrome.quit()


def to_json(html):
    soup = bs(html, 'html.parser')

    # parse data
    tp = ['theory', 'practical']
    data = dict()
    data['name'] = soup.find_all('table')[4].find_all('span')[1].text
    for k in range(2):
        tr = soup.find_all('table')[k + 6].find_all('tr')
        th = list(map(lambda x: x.text.strip(), tr[0].find_all('th')))
        data[tp[k]] = {}
        for i in range(1, len(tr)):
            td = list(map(lambda x: x.text.strip(), tr[i].find_all('td')))
            data[tp[k]][td[0]] = {}
            for j in range(1, len(th)):
                data[tp[k]][td[0]][th[j]] = td[j]
    # all_sem_gpa
    gpas = soup.find(id="ctl00_ContentPlaceHolder1_GridView3").find_all('tr')[-1].find_all('td')
    gpas = list(map(lambda x: x.text, gpas))
    data["GPA"] = gpas

    return data


class ResultObj:

    def __init__(self, reg, sem, year):
        self.reg = reg
        self.sem = sem
        self.year = year
        self.html = None
        self.json_data = None

    @property
    def result(self, save=True):
        base_link = result_links[self.year][self.sem]
        html = download_html_bs(base_link, self.reg)
        if save:
            self.html = html
        return self.html

    @property
    def jsonify(self):
        if self.html:
            data = to_json(self.html)
        else:
            data = to_json(self.result)
        self.json_data = data
        return self.json_data
