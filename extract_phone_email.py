from selenium.webdriver.common.keys import Keys
from multiprocessing import current_process
from functions import start_chrome
import os


def crawl_data(chrome, reg):
    try:
        chrome.get("http://www.akuexams.in/AKUEXAM/StudentServices/frmStudentRegistration.aspx")
        reg_inp = chrome.find_element_by_xpath('//*[@id="txtuserid"]')
        reg_inp.send_keys(reg)
        reg_inp.send_keys(Keys.ENTER)
        name = chrome.find_element_by_xpath('//*[@id="txtusername"]').get_attribute('value').upper()
        phone = chrome.find_element_by_xpath('//*[@id="txtContactNo"]').get_attribute('value')
        email = chrome.find_element_by_xpath('//*[@id="txtEmail"]').get_attribute('value').lower()
        return {
            'reg': reg,
            'name': name,
            'email': email,
            'phone': phone
        }
    except:
        return None


def extract_and_save_data(REGS, OUT_DIR_PD):
    process_name = current_process().name.lower()
    chrome = start_chrome()
    with open(os.path.join(OUT_DIR_PD, f"_{process_name}_data.csv"), "w") as f:
        f.write("REG,NAME,EMAIL,PHONE\n")

    for reg in REGS:
        try:
            sdata = crawl_data(chrome, reg)
            data = f"{sdata['reg']},{sdata['name']},{sdata['email']},{sdata['phone']}\n"
            # print(data)
            with open(os.path.join(OUT_DIR_PD, f"_{process_name}_data.csv"), "a") as f:
                f.write(data)
        except:
            # invalid reg
            pass
