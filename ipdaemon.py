#!/usr/bin/python3
# coding=utf-8
import argparse
import sys
import time
import urllib.request



import telebot
from loguru import logger

parser = argparse.ArgumentParser(add_help=True, description='ipdaemonbot Bot for Telegram')
parser.add_argument('--token', action='store', help='Authentication token [required]', required=True)
parser.add_argument('--p_login', action='store', help='Proxy login [optional]', required=False)
parser.add_argument('--p_pass', action='store', help='Proxy password [optional]', required=False)
parser.add_argument('--p_adress', action='store', help='Proxy adress [optional]', required=False)
parser.add_argument('--p_port', action='store', help='Proxy port [optional]', required=False)

args = parser.parse_args()

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
logger.add("ipdaemon.log", rotation="10 MB", enqueue=True)

if args.p_adress is not None:
    try:
        from telebot import apihelper

        apihelper.proxy = {
            'https': 'socks5h://{proxy_login}:{proxy_password}@{proxy_adress}:{proxy_port}'.format(
                proxy_login=args.p_login,
                proxy_password=args.p_pass,
                proxy_adress=args.p_adress,
                proxy_port=args.p_port)}
        logger.info("Started with proxy: {proxy_login}:{proxy_password}@{proxy_adress}:{proxy_port}".format(
            proxy_login=args.p_login,
            proxy_password=args.p_pass,
            proxy_adress=args.p_adress,
            proxy_port=args.p_port))
    except Exception as e:
        logger.exception(e)

bot_token = args.token
ipdaemonbot = telebot.TeleBot(bot_token)


@ipdaemonbot.message_handler(commands=['ip'])
@logger.catch
def get_ip(message):
    print(1)
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    ipdaemonbot.send_message(message.chat.id, external_ip)

@ipdaemonbot.message_handler(commands=['/ping'])
@logger.catch
def get_ip(message):
    ipdaemonbot.send_message(message.chat.id, "pong")

if __name__ == '__main__':

    while True:
        try:
            print(2)
            ipdaemonbot.polling(none_stop=True)
        except Exception as e:
            logger.exception(e)
            time.sleep(15)
            break