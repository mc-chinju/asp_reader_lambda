import requests
import yaml
import mechanize

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
        print(res.read())

    elif asp_name == "felmat":
    elif asp_name == "access_trade":
    elif asp_name == "mosimo":
    elif asp_name == "rentracks":

# LINE Notify settings
with open("line_notify.yml", "r") as file:
    line_pay = file.read()
LINE_TOKEN = yaml.safe_load(line_pay)["token"]
LINE_NOTIFY_URL = "https://notify-api.line.me/api/notify"

# LINe Notify logic
if LINE_TOKEN is not None:
    data = { "message": "test" }
    headers = { "Authorization": f"Bearer {LINE_TOKEN}" }

    try:
        r = requests.post(LINE_NOTIFY_URL, data=data, headers=headers)
        print(r)
    except:
        print(sys.exc_info())
