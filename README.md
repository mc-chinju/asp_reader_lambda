# asp_reader_lambda
## Python version
Only 2.x

## What's this?
This service searches ASP data.

1. Output csv data.
2. Send data to your LINE.

## How to use?
### 1. Write your personal data on `line_notify.yml` and `security.yml`
**line_notify.yml**
Duplicate this file from `line_notify.yml.sample`.
If you write your LINE token, it's enbale to send data to LINE.
[LINE Notify](https://notify-bot.line.me/) provides LINE token.

**security.yml**
Duplicate this file from `line_notify.yml.sample`.
If you write your personal ASP data, it's enbale to search data.

### 2. Install libraries

```
$ pip install -r requirements
```

### 3. Execute code

```
$ python main.py
```

The data outputs to data.csv, and send data to LINE.

## Schedule LINE Notify
1. Write `line_notify.yml` and `security.yml`.
2. `pip install -r requirements -t .`
3. Zip all files, not folder.
4. Upload the zip file to AWS Lambda, and set schedule by CloudWatch Events.
