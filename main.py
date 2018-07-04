import requests
import yaml

# settings
with open("line_notify.yml", "r") as file:
    line_pay = file.read()
LINE_TOKEN = yaml.safe_load(line_pay)["token"]
LINE_NOTIFY_URL = "https://notify-api.line.me/api/notify"

data = { "message": "test" }
headers = { "Authorization": f"Bearer {LINE_TOKEN}" }

try:
    r = requests.post(LINE_NOTIFY_URL, data=data, headers=headers)
    print(r)
except:
    print(sys.exc_info())
