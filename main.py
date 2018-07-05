import requests
import yaml
import mechanize
from bs4 import BeautifulSoup

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

            html = agent.open("%s?action=%s" % (data_page, action)).read()
            soup = BeautifulSoup(html, "html.parser")
            target = soup.select(search_target)[0]
            latest_data = target.find_all("tr")[latest_data_line]
            setattr(c, ("%s_count" % action), latest_data.find_all("td")[count_line].text.strip())
            setattr(c, ("%s_reward" % action), latest_data.find_all("td")[reward_line].text.strip())

            c.line_notify_message += asp_name.capitalize() + ":" + c.ud_reward + "\n"

    # elif asp_name == "felmat":
    # elif asp_name == "access_trade":
    # elif asp_name == "mosimo":
    # elif asp_name == "rentracks":

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
