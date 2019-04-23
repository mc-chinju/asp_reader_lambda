# coding: UTF-8

import os
import re
import time
import requests
import yaml
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from IPython import embed
from IPython.terminal.embed import InteractiveShellEmbed

## Chrome Headless Browser
chrome_options = Options()
chrome_options.set_headless(True) # If you comment out this line, Browser stands up!
# Comment out following, if you use local machine!
chrome_options.binary_location = "./bin/headless-chromium"
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--single-process")
driver_path = "./bin/chromedriver"
driver = webdriver.Chrome(driver_path, chrome_options=chrome_options)

with open("asp.yml", "r") as file:
    asp_info = yaml.safe_load(file.read())

# Securities settings
asp_names = list()
for k, v, in os.environ.items():
    if (("ASP_ID" in k) and (len(v) != 0)):
        asp_name = k.split("ASP_ID_")[1].lower()
        asp_names.append(asp_name)

# for development
# asp_names = list()
# with open("security.yml", "r") as file:
#     security_info = yaml.safe_load(file.read())
#     for asp_name in security_info.keys():
#         if security_info[asp_name]["id"]:
#             asp_names.append(asp_name)

# For instance_variable_set
class Container():
    pass
c = Container()

def initialize():
    global c
    c = Container()
    c.line_notify_message = "本日の発生報酬"

def to_num_s(str):
    return re.sub(r"\D", "", str.strip())

def delimited(str):
    return "¥{:,d}".format(int(str))

def camelize(str):
    words = str.split("_")
    return words[0].capitalize() + "".join(x.title() for x in words[1:])

def add_line_message(asp_name, message):
    c.line_notify_message += "\n" + camelize(asp_name) + ": " + message

def search_asps():
    for asp_name in asp_names:
        login_page = asp_info[asp_name]["login"]
        data_page = asp_info[asp_name]["data"]
        # for development
        # login_id = security_info[asp_name]["id"]
        # password = security_info[asp_name]["password"]
        login_id = os.environ[f"ASP_ID_{asp_name.upper()}"]
        password = os.environ[f"ASP_PW_{asp_name.upper()}"]

        print("%sのデータ検索を開始します。" % camelize(asp_name))
        if asp_name == "a8":
            try:
                driver.get(login_page)
                driver.find_element_by_name("login").send_keys(login_id)
                driver.find_element_by_name("passwd").send_keys(password)
                driver.find_element_by_name("lgin_as_btn").click()

                time.sleep(3) # js読み込みが終わるまでのバッファ
                html = driver.page_source.encode("utf-8")
                soup = BeautifulSoup(html, "html.parser")
                target = soup.select("#reportBox01 .repo03 td")
                price = to_num_s(target[0].text)
                add_line_message(asp_name, delimited(price))
            except:
                add_line_message(asp_name, "取得失敗")

        elif asp_name == "felmat":
            try:
                driver.get(login_page)
                driver.find_element_by_name("p_username").send_keys(login_id)
                driver.find_element_by_name("p_password").send_keys(password)
                driver.find_element_by_name("partnerlogin").click()

                driver.get(f"{data_page}/daily")
                time.sleep(3) # js読み込みが終わるまでのバッファ
                html = driver.page_source.encode("utf-8")
                soup = BeautifulSoup(html, "html.parser")

                today_number = datetime.date.today().day
                target_line = soup.find_all("tbody")[0].find_all("tr")[-today_number]
                price = to_num_s(target_line.find_all("td")[5].text)
                add_line_message(asp_name, delimited(price))
            except:
                add_line_message(asp_name, "取得失敗")

        elif asp_name == "access_trade":
            try:
                driver.get(login_page)
                driver.find_element_by_name("userId").send_keys(login_id)
                driver.find_element_by_name("userPass").send_keys(password)
                driver.find_element_by_xpath("//form[@action='https://member.accesstrade.net/atv3/login.html']/input[@class='btn']").click()

                time.sleep(3) # js読み込みが終わるまでのバッファ
                html = driver.page_source.encode("utf-8")
                soup = BeautifulSoup(html, "html.parser")
                target = soup.select(".report tbody tr")
                price = to_num_s(target[2].find_all("td")[0].text)
                add_line_message(asp_name, delimited(price))
            except:
                add_line_message(asp_name, "取得失敗")

        elif asp_name == "mosimo":
            try:
                driver.get(login_page)
                driver.find_element_by_name("account").send_keys(login_id)
                driver.find_element_by_name("password").send_keys(password)
                driver.find_element_by_name("login").click()

                driver.get(f"{data_page}/daily")
                time.sleep(3) # js読み込みが終わるまでのバッファ

                html = driver.page_source.encode("utf-8")
                soup = BeautifulSoup(html, "html.parser")
                target = soup.select(".payment-table tbody")[0].find_all("tr")[-1]
                price = to_num_s(target.find_all("td")[3].find_all("p")[1].text)
                add_line_message(asp_name, delimited(price))
            except:
                add_line_message(asp_name, "取得失敗")

        elif asp_name == "rentracks":
            try:
                driver.get(login_page)
                driver.find_element_by_name("idMailaddress").send_keys(login_id)
                driver.find_element_by_name("idLoginPassword").send_keys(password)
                driver.find_element_by_name("idButton").click()

                driver.get(data_page)
                time.sleep(3) # js読み込みが終わるまでのバッファ

                html = driver.page_source.encode("utf-8")
                soup = BeautifulSoup(html, "html.parser")
                target = soup.select(".datatable tr")

                price = to_num_s(target[9].find_all("td")[5].text)
                add_line_message(asp_name, delimited(price))
            except:
                add_line_message(asp_name, "取得失敗")

        elif asp_name == "value_commerce":
            try:
                # Login
                driver.get(login_page)
                driver.find_element_by_id("login_form_emailAddress").send_keys(login_id)
                driver.find_element_by_id("login_form_encryptedPasswd").send_keys(password)
                driver.find_element_by_class_name("btn_green").click()

                # Get data
                driver.get(data_page)
                html = driver.page_source.encode("utf-8")
                soup = BeautifulSoup(html, "html.parser")
                target = soup.select("#report tbody tr")[1]
                price = to_num_s(target.find_all("td")[8].text)
                add_line_message(asp_name, delimited(price))
            except:
                add_line_message(asp_name, "取得失敗")

        # TODO: headless mode で動かしたときに、ログイン時にランダム文字列入力を求められるため断念
        # elif asp_name == "amazon_associate":
        #     try:
        #         # Login
        #         driver.get(login_page)
        #         driver.find_element_by_name("email").send_keys(login_id)
        #         driver.find_element_by_name("password").send_keys(password)
        #         driver.find_element_by_id("signInSubmit").click()
        #
        #         # 当日のデータがリアルタイムで出ないので、昨日のデータを取得
        #         driver.get(data_page)
        #         element = driver.find_element_by_id("ac-daterange-label-report-timeInterval")
        #         hov = ActionChains(driver).move_to_element(element)
        #         hov.perform()
        #
        #         time.sleep(3) # 読み込みが終わるまでのバッファ
        #
        #         driver.find_element_by_id("ac-daterange-radio-report-timeInterval-yesterday").click()
        #         driver.find_element_by_id("ac-daterange-ok-button-report-timeInterval-announce").click()
        #
        #         time.sleep(3) # 読み込みが終わるまでのバッファ
        #
        #         html = driver.page_source.encode("utf-8")
        #         soup = BeautifulSoup(html, "html.parser")
        #
        #         target = soup.select("#ac-report-earning-amount")
        #         price = to_num_s(target[0].text)
        #         add_line_message(asp_name, delimited(price))
        #     except:
        #         add_line_message(asp_name, "取得失敗")

        # TODO: 売上がゼロのためhtml構造がわからず結果の出力ができない
        # elif asp_name == "presco":
        #     try:
        #         # Login
        #         driver.get(login_page)
        #         driver.find_elements_by_xpath("//input[@name='username']")[1].send_keys(login_id)
        #         driver.find_elements_by_xpath("//input[@name='password']")[1].send_keys(password)
        #         driver.find_elements_by_xpath("//input[@type='submit']")[1].click()
        #
        #         driver.get(data_page)
        #         html = driver.page_source.encode("utf-8")
        #         soup = BeautifulSoup(html, "html.parser")
        #
        #         # target = soup.select("#mainContents tbody tr")[now.day + 1]
        #         # price = to_num_s(target.find_all("td")[-1].text)
        #         add_line_message(asp_name, delimited(price))
        #     except:
        #         add_line_message(asp_name, "取得失敗")

def line_notify():
    # LINE Notify settings

    # for development
    # with open("line_notify.yml", "r") as file:
    #     line_notify = file.read()
    # LINE_TOKEN = yaml.safe_load(line_notify)["token"]

    LINE_TOKEN = os.environ["LINE_NOTIFY_TOKEN"]
    LINE_NOTIFY_URL = "https://notify-api.line.me/api/notify"

    # LINe Notify logic
    if LINE_TOKEN is not None:
        data = { "message": c.line_notify_message }
        headers = { "Authorization": "Bearer %s" % LINE_TOKEN }

        try:
            r = requests.post(LINE_NOTIFY_URL, data=data, headers=headers)
            print("%s LINE通知" % r)
        except:
            print(sys.exc_info())

def lambda_handler(event, context):
    initialize()
    search_asps()
    line_notify()
