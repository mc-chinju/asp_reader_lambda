# coding: UTF-8

import re
import requests
import yaml
import mechanize
from bs4 import BeautifulSoup

# For debug
from IPython import embed
from IPython.terminal.embed import InteractiveShellEmbed

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
c.line_notify_message = "本日の発生報酬"

def to_num_s(str):
    return re.sub(r"\D", "", str.strip().encode("utf-8"))

def camelize(str):
    words = str.split("_")
    return words[0].capitalize() + "".join(x.title() for x in words[1:])

def search_asps():
    for asp_name in asp_names:
        login_page = asp_info[asp_name]["login"]
        data_page = asp_info[asp_name]["data"]
        login_id = security_info[asp_name]["id"]
        password = security_info[asp_name]["password"]

        agent.open(login_page)

        print("%sのデータ検索を開始します。" % camelize(asp_name))

        if asp_name == "a8":
            agent.select_form(name="asLogin")
            agent["login"] = login_id
            agent["passwd"] = password
            agent.submit()

            action = "ud"
            latest_data_line = 2
            search_target = ".reportTable1"

            count_line = 5
            reward_line = 6

            html = agent.open("%s?action=%s" % (data_page, action))
            soup = BeautifulSoup(html, "html.parser")
            target = soup.select(search_target)[0]
            latest_data = target.find_all("tr")[latest_data_line]
            setattr(c, ("%s_reward" % action), to_num_s(latest_data.find_all("td")[reward_line].text))

        elif asp_name == "felmat":
            agent.select_form(name="loginForm")
            agent["p_username"] = login_id
            agent["p_password"] = password
            agent.submit()

            actions = ["daily", "monthly"]
            for action in actions:
                html = agent.open("%s/%s" % (data_page, action))
                soup = BeautifulSoup(html, "html.parser")
                target = soup.find_all("tbody")[0]
                latest_data = target.find_all("tr")[0]
                term = "d" if action == "daily" else "m"
                if (term == "d"):
                    setattr(c, "ud_reward", to_num_s(latest_data.find_all("td")[5].text))

        elif asp_name == "access_trade":
            form_action = "https://member.accesstrade.net/atv3/login.html"
            agent.select_form(action=form_action)
            agent["userId"] = login_id
            agent["userPass"] = password
            agent.submit()

            html = agent.open(data_page)
            soup = BeautifulSoup(html, "html.parser")
            target = soup.select(".report tbody tr")
            setattr(c, "ud_reward", to_num_s(target[2].find_all("td")[0].text))

        elif asp_name == "mosimo":
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
                    setattr(c, "ud_reward", to_num_s(target.find_all("td")[3].find_all("p")[1].text))

        elif asp_name == "rentracks":
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
                    setattr(c, "ud_reward", to_num_s(target[4].find_all("td")[5].text))

        c.line_notify_message += "\n" + camelize(asp_name) + ": ¥{:,d}".format(int(c.ud_reward))

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
    search_asps()
    line_notify()
