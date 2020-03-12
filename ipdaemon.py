#!/usr/bin/python3
# coding=utf-8
# code for win service - http://iqa.com.ua/programming/python/windows-services-from-python-scripts

import win32serviceutil
import win32service
import win32event
import servicemanager

import argparse
import sys
import urllib.request
from telebot import apihelper

import telebot
from loguru import logger


class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "Get IP Daemon"
    _svc_display_name_ = "Get IP Daemon"
    _svc_description_ = "Get IP Daemon"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.hWaitResume = win32event.CreateEvent(None, 0, 0, None)
        self.timeout = 10000  # Пауза между выполнением основного цикла службы в миллисекундах
        self.resumeTimeout = 1000
        self._paused = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STOPPED,
                              (self._svc_name_, ''))

    def SvcPause(self):
        self.ReportServiceStatus(win32service.SERVICE_PAUSE_PENDING)
        self._paused = True
        self.ReportServiceStatus(win32service.SERVICE_PAUSED)
        servicemanager.LogInfoMsg("The %s service has paused." % (self._svc_name_,))

    def SvcContinue(self):
        self.ReportServiceStatus(win32service.SERVICE_CONTINUE_PENDING)
        win32event.SetEvent(self.hWaitResume)
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        servicemanager.LogInfoMsg("The %s service has resumed." % (self._svc_name_,))

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        # Здесь выполняем необходимые действия при старте службы
        bot_token = ''
        proxy_login = ''
        proxy_password = ''
        proxy_adress = '',
        proxy_port = ''

        apihelper.proxy = {
            'https': 'socks5h://{proxy_login}:{proxy_password}@{proxy_adress}:{proxy_port}'.format(
                proxy_login=proxy_login,
                proxy_password=proxy_password,
                proxy_adress=proxy_adress,
                proxy_port=proxy_port)}

        ipdaemonbot = telebot.TeleBot(bot_token)

        @ipdaemonbot.message_handler(commands=['ip'])
        @logger.catch
        def get_ip(message):
            print(1)
            external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
            ipdaemonbot.send_message(message.chat.id, external_ip)

        servicemanager.LogInfoMsg("Hello! Get IP Daemon here.")
        while True:
            # Здесь должен находиться основной код сервиса
            servicemanager.LogInfoMsg("I'm still here.")

            ipdaemonbot.polling(none_stop=True)

            # Проверяем не поступила ли команда завершения работы службы
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:
                # Здесь выполняем необходимые действия при остановке службы
                servicemanager.LogInfoMsg("Bye!")
                break

            # Здесь выполняем необходимые действия при приостановке службы
            if self._paused:
                servicemanager.LogInfoMsg("I'm paused... Keep waiting...")
            # Приостановка работы службы
            while self._paused:
                # Проверям не поступила ли команда возобновления работы службы
                rc = win32event.WaitForSingleObject(self.hWaitResume, self.resumeTimeout)
                if rc == win32event.WAIT_OBJECT_0:
                    self._paused = False
                    # Здесь выполняем необходимые действия при возобновлении работы службы
                    servicemanager.LogInfoMsg("Yeah! Let's continue!")
                    break


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
