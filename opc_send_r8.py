# -*- coding: utf-8 -*-
import threading
from opc_send_functions import *
import pywintypes
from enum import Enum
from pathlib import Path
import yaml
import requests
import telebot
import OpenOPC
import time

pywintypes.datetime = pywintypes.TimeType

server = ''
tagsValue = []
thresholds = []

def read_config():
    config = Path('config2.yaml').read_text(encoding='utf-8')
    return yaml.safe_load(config)

app_config = read_config()
thresholds_config = app_config['thresholds']

class ThresholdChecker:

    def __init__(self, cfg):
        # for k in cfg.keys():
        #     self.__dict__[k] = cfg[k]

        self.parameter_name = cfg['name']
        self.opc_data_index = cfg['opc_data_index']
        self.base_value = cfg['base_value']
        self.deviation = cfg['deviation']
        self.lower_message_template = cfg['lower_message_template']
        self.upper_message_template = cfg['upper_message_template']

        self.upper_limit = int(self.base_value) + int(self.deviation)
        self.lower_limit = self.base_value - self.deviation
        self.result = None

    def check_threshold(self, opc_data):
        opc_value = opc_data[self.opc_data_index]
        if opc_value > self.upper_limit:
            self.result = CheckResult.HIGHER
        elif opc_value < self.lower_limit:
            self.result = CheckResult.LOWER
        else:
            self.result = CheckResult.OK

    def _lower_limit_message(self, opc_data):
        return self.lower_message_template.format(opc_data[self.opc_data_index])

    def _upper_limit_message(self, opc_data):
        return self.upper_message_template.format(opc_data[self.opc_data_index])

    def message(self, opc_data):
        if self.result == CheckResult.LOWER:
            return self._lower_limit_message(opc_data)
        elif self.result == CheckResult.HIGHER:
            return self._upper_limit_message(opc_data)
        else:
            return None
    def print(self):
        print(self.parameter_name,
        self.opc_data_index,
        self.base_value,
        self.deviation,
        self.lower_message_template,
        self.upper_message_template,

        self.upper_limit,
        self.lower_limit,
        self.result)


with open(r"tags.txt", "r", encoding="utf-8") as file:
    # Получаем словарь из txt-файла. Этот словать нужен для отправки сообщений телеграм
    tags = file.read()
    allValue = tags.split("\n")
    tg_lst = {}
    server = allValue[0].split(',')[1]
    i = 0
    j = 0
    for el in allValue:
        el = el.split(",")
        tg_lst[el[0]] = el[1]
        if i == 0:
            i += 1
            continue
        try:
            thresholds.append(ThresholdChecker(thresholds_config[el[2]]))
            thresholds[j].opc_data_index = i
            j += 1
        except KeyError as err:
            i += 1
            continue
        tagsValue.append(el[1])
        i += 1
print(tagsValue)
# print(tagsValue)
# for name, el in tg_lst.items():
#     print(name, el)
print(thresholds)

class CheckResult(Enum):
    OK = 1
    HIGHER = 2
    LOWER = 3


# for (threshold_key) in thresholds_config:
#     thresholds.append(ThresholdChecker(threshold_key))


TOKEN = config['token']


def run_setting(tagsValue, tg_lst):
    """
    Telegram_bot functions:
    start_message() - get data
    query_handler() - send data
    """
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def start_message(message):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(
            text='Получить параметры реактора Р-8', callback_data=3))
        bot.send_message(message.chat.id, text="Что вы хотите сделать?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def query_handler(call):
        answer = ''
        if call.data == '3':
            try:
                opc1 = OpenOPC.client()
                opc1.connect(tagsValue[0])
                # tag1 = opc1.list("COM4.TRM_202(adr=104)T_слой_Ср_р-ра.Оперативные параметры")[3]
                answer = opc1.read(tagsValue, update=1, include_error=True)
                print(answer)
                opc1.close()
                count = 0
                while count < len(tagsValue):
                    bot.send_message(call.message.chat.id,
                                     "{0:_^20} {1:>10.2f}".format(tg_lst[tagsValue[count]], answer[count][1]))
                    count += 1
            except ConnectionError as err:
                print(err)

    bot.polling()


def send_telegram(text: str, TOKEN):
    '''
    function take arg 'str' and send in telegram
    :return:
    '''
    url = "https://api.telegram.org/bot"
    channel_id = config['channel_id']
    url += TOKEN
    method = url + "/sendMessage"

    req = requests.post(method, data={
        "chat_id": channel_id,
        "text": text
    })
    if req.status_code != 200:
        print("Ошибка отправки сообщения в тг")


def send_mess(server, tagsValue, poll_time):
    '''
    Send message in telegram
    if parameter goes abroad
    '''
    while True:
        # def opc_connect(tag):
        #     opc.connect(server)
        #     val = opc.read(tagsValue, update=1, include_error=True)
        #     if val > thresholds[find_struct(tag)].upper_limit:
        #         send_telegram(thresholds[find_struct(tag)].message(val))
        #     if val < thresholds[find_struct(tag)].lower_limit:
        #         send_telegram(thresholds[find_struct(tag)].message(val)

        with OpenOPC.client() as opc:
            opc.connect(server)
            val = opc.read(tagsValue, update=1, include_error=True)
            for el in thresholds:
                if val[el.opc_data_index][1] > el.upper_limit:
                    send_telegram(el.upper_message_template, TOKEN)
                if val[el.opc_data_index][1] < el.lower_limit:
                    send_telegram(el.lower_message_template, TOKEN)

        time.sleep(poll_time)


thrd_send_mess = threading.Thread(target=send_mess(server, tagsValue, app_config['poll_frequency_seconds']))
thrd_send_mess.start()
thrd_run_setting = threading.Thread(target=run_setting(tagsValue, tg_lst))
thrd_run_setting.start()
