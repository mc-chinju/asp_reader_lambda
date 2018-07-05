# coding: UTF-8

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
c.line_notify_message = "Today\n"

for asp_name in asp_names:
    login_page = asp_info[asp_name]["login"]
    data_page = asp_info[asp_name]["data"]
    login_id = security_info[asp_name]["id"]
    password = security_info[asp_name]["password"]

    agent.open(login_page)

    print("%sのデータ検索を開始します。" % asp_name.capitalize())

    if asp_name == "a8":
        agent.select_form(name="asLogin")
        agent["login"] = login_id
        agent["passwd"] = password
        agent.submit()

        # unconfirmed => u, decided => d
        # month => m, daily => d
        actions = ["ud", "dd", "um", "dm"]
        for action in actions:
            latest_data_line = 1 if action in ["um", "dm"] else 2
            search_target = "table" if (action == "dd") else ".reportTable1"

            if action == "ud":
                count_line = 5
                reward_line = 6
            elif action in ["dd", "um"]:
                count_line = 3
                reward_line = 4
            elif action == "dm":
                count_line = 1
                reward_line = 2

            html = agent.open("%s?action=%s" % (data_page, action))
            soup = BeautifulSoup(html, "html.parser")
            target = soup.select(search_target)[0]
            latest_data = target.find_all("tr")[latest_data_line]
            setattr(c, ("%s_count" % action), latest_data.find_all("td")[count_line].text.strip())
            setattr(c, ("%s_reward" % action), latest_data.find_all("td")[reward_line].text.strip())

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
            setattr(c, "u%s_count" % term, latest_data.find_all("td")[4].text.strip())
            setattr(c, "u%s_reward" % term, latest_data.find_all("td")[5].text.strip())
            setattr(c, "d%s_count" % term, latest_data.find_all("td")[7].text.strip())
            setattr(c, "d%s_reward" % term, latest_data.find_all("td")[8].text.strip())

    elif asp_name == "access_trade":
        form_action = "https://member.accesstrade.net/atv3/login.html"
        agent.select_form(action=form_action)
        agent["userId"] = login_id
        agent["userPass"] = password
        agent.submit()

        html = agent.open(data_page)
        soup = BeautifulSoup(html, "html.parser")
        target = soup.select(".report tbody tr")
        setattr(c, "ud_count", target[1].find_all("td")[0].text)
        setattr(c, "um_count", target[1].find_all("td")[1].text)
        setattr(c, "ud_reward", target[2].find_all("td")[0].text.strip())
        setattr(c, "um_reward", target[2].find_all("td")[1].text.strip())
        setattr(c, "dd_count", target[3].find_all("td")[0].text)
        setattr(c, "dm_count", target[3].find_all("td")[1].text)
        setattr(c, "dd_reward", target[4].find_all("td")[0].text.strip())
        setattr(c, "dm_reward", target[4].find_all("td")[1].text.strip())

    elif asp_name == "mosimo":
        agent.select_form(id="login-form")
        agent["account"] = login_id
        agent["password"] = password
        agent.submit()

        actions = ["daily", "monthly"]
        for action in actions:
            html = agent.open("%s/%s" % (data_page, action))
            soup = BeautifulSoup(html, "html.parser")
            target = soup.select(".payment-table tbody")[0].find_all("tr")[-1]
            term = "d" if action == "daily" else "m"
            setattr(c, "u%s_count" % term, target.find_all("td")[3].find_all("p")[0].text.strip())
            setattr(c, "u%s_reward" % term, target.find_all("td")[3].find_all("p")[1].text.strip())
            setattr(c, "d%s_count" % term, target.find_all("td")[4].find_all("p")[0].text.strip())
            setattr(c, "d%s_reward" % term, target.find_all("td")[4].find_all("p")[1].text.strip())

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
            setattr(c, "u%s_count" % term, target[4].find_all("td")[3].text.strip())
            setattr(c, "u%s_reward" % term, target[4].find_all("td")[5].text.strip())
            setattr(c, "d%s_count" % term, target[7].find_all("td")[3].text.strip())
            setattr(c, "d%s_reward" % term, target[7].find_all("td")[5].text.strip())

    c.line_notify_message += asp_name.capitalize() + ":" + c.ud_reward + "\n"

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
        print(r)
    except:
        print(sys.exc_info())
