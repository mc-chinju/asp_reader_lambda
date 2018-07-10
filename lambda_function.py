# coding: UTF-8

import re
import requests
import yaml
import mechanize
import datetime
from bs4 import BeautifulSoup

# For debug
# from IPython import embed
# from IPython.terminal.embed import InteractiveShellEmbed

# Scraping Settings
agent = mechanize.Browser()
agent.addheaders = [("User-agent", "Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.4b) Gecko/20030516 Mozilla Firebird/0.6")]
agent.set_handle_robots(False)
with open("asp.yml", "r") as file:
    asp_info = yaml.safe_load(file.read())

# Securities settings
asp_names = list()
with open("security.yml", "r") as file:
    security_info = yaml.safe_load(file.read())
    # TODO: refactoring code!
    # Select target asps
    for asp_name in security_info.keys():
        if security_info[asp_name]["id"]:
            asp_names.append(asp_name)

# For instance_variable_set
class Container():
    pass
c = Container()

def initialize():
    global c
    c = Container()
    c.line_notify_message = "本日の発生報酬"

def to_num_s(str):
    return re.sub(r"\D", "", str.strip().encode("utf-8"))

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
        login_id = security_info[asp_name]["id"]
        password = security_info[asp_name]["password"]

        agent.open(login_page)

        print("%sのデータ検索を開始します。" % camelize(asp_name))

        # A8 は当日のデータをjsで描画しているため、現状の仕組みでは取得できず。
        # if asp_name == "a8":
        #     try:
        #         agent.select_form(name="asLogin")
        #         agent["login"] = login_id
        #         agent["passwd"] = password
        #         agent.submit()
        #
        #         action = "ud"
        #         latest_data_line = 2
        #         search_target = ".reportTable1"
        #
        #         reward_line = 6
        #
        #         html = agent.open("%s?action=%s" % (data_page, action))
        #         soup = BeautifulSoup(html, "html.parser")
        #         target = soup.select(search_target)[0]
        #         latest_data = target.find_all("tr")[latest_data_line]
        #         price = to_num_s(latest_data.find_all("td")[reward_line].text)
        #         add_line_message(asp_name, delimited(price))
        #     except:
        #         add_line_message(asp_name, "取得失敗")

        if asp_name == "felmat":
            try:
                agent.select_form(name="loginForm")
                agent["p_username"] = login_id
                agent["p_password"] = password
                agent.submit()

                html = agent.open("%s/%s" % (data_page, "daily"))
                soup = BeautifulSoup(html, "html.parser")

                today_number = datetime.date.today().day
                target_line = soup.find_all("tbody")[0].find_all("tr")[-today_number]
                price = to_num_s(target_line.find_all("td")[5].text)
                add_line_message(asp_name, delimited(price))
            except:
                add_line_message(asp_name, "取得失敗")

        elif asp_name == "access_trade":
            try:
                form_action = "https://member.accesstrade.net/atv3/login.html"
                agent.select_form(action=form_action)
                agent["userId"] = login_id
                agent["userPass"] = password
                agent.submit()

                html = agent.open(data_page)
                soup = BeautifulSoup(html, "html.parser")
                target = soup.select(".report tbody tr")
                price = to_num_s(target[2].find_all("td")[0].text)
                add_line_message(asp_name, delimited(price))
            except:
                add_line_message(asp_name, "取得失敗")

        elif asp_name == "mosimo":
            try:
                form_action = "https://af.moshimo.com/af/shop/login/execute"
                agent.select_form(action=form_action)
                agent["account"] = login_id
                agent["password"] = password
                agent.submit()

                actions = ["daily", "monthly"]
                for action in actions:
                    html = agent.open("%s/%s" % (data_page, action))
                    soup = BeautifulSoup(html, "html.parser")
                    target = soup.select(".payment-table tbody")[0].find_all("tr")[-1]
                    term = "d" if action == "daily" else "m"
                    if (term == "d"):
                        price = to_num_s(target.find_all("td")[3].find_all("p")[1].text)
                        add_line_message(asp_name, delimited(price))
            except:
                add_line_message(asp_name, "取得失敗")

        elif asp_name == "rentracks":
            try:
                form_action = "https://manage.rentracks.jp/manage/login/login_manage_validation"
                agent.select_form(action=form_action)
                agent["idMailaddress"] = login_id
                agent["idLoginPassword"] = password
                agent.submit()

                html = agent.open(data_page)
                soup = BeautifulSoup(html, "html.parser")
                target = soup.select(".datatable tr")

                actions = ["daily", "monthly"]
                for action in actions:
                    term = "d" if action == "daily" else "m"
                    if (term == "d"):
                        price = to_num_s(target[4].find_all("td")[5].text)
                        add_line_message(asp_name, delimited(price))
            except:
                add_line_message(asp_name, "取得失敗")

def line_notify():
    # LINE Notify settings
    with open("line_notify.yml", "r") as file:
        line_pay = file.read()
    LINE_TOKEN = yaml.safe_load(line_pay)["token"]
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
