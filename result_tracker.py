from selenium.webdriver.common.keys import Keys
from urllib.request import urlopen
import random, json, time, os, sys
from vars import bce_reg_list
from functions import start_chrome


def get_initial_state(result_link):
    chrome = start_chrome()
    chrome.get(result_link)
    _html = chrome.page_source
    _tr_list = chrome.execute_script(
        """return document.querySelector('table[class="style1"]').querySelectorAll('tr')""")
    _tr_texts = list(map(lambda x: x.text, _tr_list))
    chrome.quit()
    return {
        '_html': _html,
        '_tr_texts': _tr_texts
    }


def find_sem(text):
    sem_map = {'1st': 'sem1', '2nd': 'sem2', '3rd': 'sem3',
               '4th': 'sem4', '5th': 'sem5', '6th': 'sem6'}
    keywords = ['b.tech', 'b. tech', 'btech', 'b tech']
    is_btech_result = False
    for key in keywords:
        if key in text.lower():
            is_btech_result = True
            break

    data = {
        "is_btech_result": is_btech_result,
    }

    for key, value in sem_map.items():
        if key in text.lower():
            data['sem'] = value
            break

    if 'sem' not in data:
        data['sem'] = None
    return data


def _updated(chrome, _html, link, lib='chrome'):
    if lib == 'chrome':
        chrome.get(link)
        return _html != chrome.page_source
    else:
        return _html != urlopen(link).read()


def find_new_elements(chrome, _tr_texts):
    tr_list = chrome.execute_script(
        """return document.querySelector('table[class="style1"]').querySelectorAll('tr')""")
    new_elements = [i for i in range(len(tr_list))
                    if tr_list[i].text not in _tr_texts]

    return new_elements


def get_result_links(chrome, link, el_ids):
    random_regs = [bce_reg_list[random.randint(0, len(bce_reg_list))]
                   for i in range(2)]
    for tr_id in el_ids:
        chrome.get(link)
        tr_list = chrome.execute_script(
            """return document.querySelector('table[class="style1"]').querySelectorAll('tr')""")
        new_tr = tr_list[tr_id]
        sem_data = find_sem(new_tr.text)

        new_tr.click()
        tr_link = chrome.current_url
        for reg in random_regs:
            chrome.get(tr_link)

            # enter reg no. and submit
            reg_inp = chrome.find_element_by_id("ctl00_ContentPlaceHolder1_TextBox_RegNo")
            reg_inp.send_keys(reg)
            reg_inp.send_keys(Keys.ENTER)
            if "New Official Website of Aryabhatta Knowledge University" in chrome.page_source:
                return {
                    "sem": sem_data['sem'],
                    "is_btech_result": sem_data['is_btech_result'],
                    "form_link": tr_link,
                    "res_link": chrome.current_url,
                    "base_res_link": chrome.current_url.rstrip(str(reg))
                }

            return None


def update_link_json(data):
    link_json = os.path.join('data', 'output', 'extracted_links.json')
    with open(link_json, 'r') as f:
        js = json.load(f)
    js.append(data)
    with open(link_json, 'w') as f:
        json.dump(js, f, indent=4)
