from datetime import date, datetime, timedelta
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
# import pytz

# Set the timezone to New York
# ny_tz = pytz.timezone('America/New_York')
# ny_time = datetime.datetime.now(ny_tz)
# today = ny_time.strftime('%Y-%m-%d %H:%M)

# nowtime = datetime.utcnow() - timedelta(hours=5)  # New york time
nowtime = datetime.utcnow() - timedelta(hours=5)
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d") #今天的日期

start_date = os.environ['START_DATE']
# city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_ids = os.getenv('USER_ID', '').split("\n")
template_id = os.environ["TEMPLATE_ID"]


# def get_weather():
#   url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
#   res = requests.get(url).json()
#   weather = res['data']['list'][0]
#   return weather['weather'], math.floor(weather['temp'])

def get_week_day():
  week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
  week_day = week_list[datetime.date(today).weekday()]
  return week_day
  
def get_anniversary_day_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def split_message(message, limit):
    return [message[i:i+limit] for i in range(0, len(message), limit)]
  
def get_sweet_words():
  words = requests.get("https://api.shadiao.pro/chp")
  return words.json()['data']['text']

def get_wit_words():
  #   words = requests.get("https://api.shadiao.pro/du")
  #   if words.status_code != 200:
  #     return get_words()
  #   return words.json()['data']['text']
  words = requests.get("https://api.shadiao.pro/du")
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
# wea, temperature = get_weather()
# data = {"weather":{"value":wea},"temperature":{"value":temperature},"love_days":{"value":get_count()},"birthday_left":{"value":get_birthday()},"words":{"value":get_words(), "color":get_random_color()}}
# Start by initializing the base dictionary
data = {
  "date": {"value": today.strftime('%Y年%m月%d日')},
  "week_day": {"value": get_week_day()},
  "love_days":{"value": get_anniversary_day_count()},
  "birthday_left":{"value": get_birthday()},
}

# Define a maximum character limit for each field
character_limit = 20

# Split the 'sweet_words' and 'wit_words' values into multiple parts
sweet_words_parts = split_message(get_sweet_words(), character_limit)
wit_words_parts = split_message(get_wit_words(), character_limit)

# Add each part to the dictionary as a separate field
for i, part in enumerate(sweet_words_parts):
    field_name = f"sweet_words_{i+1}"
    data[field_name] = {"value": part}

for i, part in enumerate(wit_words_parts):
    field_name = f"wit_words_{i+1}"
    data[field_name] = {"value": part}

# res = wm.send_template(user_id, template_id, data)
# print(res)

if __name__ == '__main__':
  count = 0
  try:
    for user_id in user_ids:
      res = wm.send_template(user_id, template_id, data)
      print(data)
      count+=1
  except WeChatClientException as e:
    print('微信端返回错误：%s。错误代码：%d' % (e.errmsg, e.errcode))
    exit(502)

  print("发送了" + str(count) + "条消息")
