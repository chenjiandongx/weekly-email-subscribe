# !/usr/bin/env python
# coding=utf-8

import datetime
import os
import re
import smtplib
from email.header import Header
from email.mime.text import MIMEText

import requests
from tenacity import retry, stop_after_attempt

from receivers import MAIL_RECEIVER

START_URL = "https://github.com/ruanyf/weekly"
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
}

# 隐私数据存放在环境变量中
MAIL_HOST = os.environ.get("MAIL_HOST")
MAIL_USER = os.environ.get("MAIL_USER")
MAIL_PASS = os.environ.get("MAIL_PASS")
MAIL_SENDER = os.environ.get("MAIL_SENDER")

MAIL_ENCODING = "utf8"


def is_saturday():
    """
    判断是否周六
    """
    return datetime.datetime.now().weekday() == 5


@retry(stop=stop_after_attempt(3))
def get_email_content():
    """
    获取邮件内容
    """
    resp = requests.get(START_URL, headers=HEADERS).text
    result = re.findall(r'<a href="(.*?\.md)">(.*?)</a>', resp)
    url, num = result[0]

    html = """
        <html lang="en">
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            <div>
                <a href="{0}">📅 阮一峰技术周刊{1}</a>
            <div>
        </body>
        </html>
    """
    return html.format("https://github.com/" + url, num)


def send_email():
    """
    发送邮件
    """
    if not is_saturday():
        return

    content = get_email_content()
    message = MIMEText(content, "html", MAIL_ENCODING)
    message["From"] = Header("weekly-bot", MAIL_ENCODING)
    message["To"] = Header("Reader")
    message["Subject"] = Header("weekly", MAIL_ENCODING)
    try:
        smtp_obj = smtplib.SMTP_SSL(MAIL_HOST)
        smtp_obj.login(MAIL_USER, MAIL_PASS)
        smtp_obj.sendmail(MAIL_SENDER, MAIL_RECEIVER, message.as_string())
        smtp_obj.quit()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    send_email()
