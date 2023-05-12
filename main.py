import asyncio
import aiohttp
from datetime import date, datetime, timedelta
import math
import os
import random
import requests
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
user_ids = os.getenv('USER_ID', '').split("\n")
template_id = os.environ["TEMPLATE_ID"]
start_date = os.environ['START_DATE']
birthday = os.environ['BIRTHDAY']

# Calculate New York time
nowtime = datetime.utcnow() - timedelta(hours=5)
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")

def split_message(message, limit):
    return [message[i:i+limit] for i in range(0, len(message), limit)]

def get_week_day():
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return week_list[today.weekday()]

def get_anniversary_day_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days

def get_birthday():
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    return (next - today).days

async def get_sweet_words():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.shadiao.pro/chp') as resp:
            words = await resp.json()
            return words['data']['text']

async def get_wit_words():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.shadiao.pro/du') as resp:
            words = await resp.json()
            return words['data']['text']

async def send_multiple_messages(message_parts, field_name):
    for i, part in enumerate(message_parts):
        data = {
            "date": {"value": today.strftime('%Y年%m月%d日')},
            "week_day": {"value": get_week_day()},
            "love_days":{"value": get_anniversary_day_count()},
            "birthday_left":{"value": get_birthday()},
        }
        data[field_name] = {"value": part}
        for user_id in user_ids:
            res = wm.send_template(user_id, template_id, data)
            print(data)

if __name__ == '__main__':
    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)

    character_limit = 20

    loop = asyncio.get_event_loop()

    sweet_words_parts = loop.run_until_complete(get_sweet_words())
    sweet_words_parts = split_message(sweet_words_parts, character_limit)

    wit_words_parts = loop.run_until_complete(get_wit_words())
    wit_words_parts = split_message(wit_words_parts, character_limit)

    tasks = [
        send_multiple_messages(sweet_words_parts, "sweet_words"),
        send_multiple_messages(wit_words_parts, "wit_words")
    ]

    loop.run_until_complete(asyncio.gather(*tasks))
