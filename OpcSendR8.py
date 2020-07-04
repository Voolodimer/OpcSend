# -*- coding: utf-8 -*-
import OpenOPC
import time
import requests
import telebot
import threading

import pywintypes
pywintypes.datetime = pywintypes.TimeType
token = "1203397890:AAF3Z53lbtmCWkXlsxJl4fXRj6Dtcv6TEc0"
###################################################
#
def run_setting():
    bot = telebot.TeleBot(token)
    @bot.message_handler(commands=['start'])
    def start_message(message):
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        #bot.send_message(message.chat.id, 'Привет!', reply_markup=keyboard)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='Получить параметры реактора Р-8', callback_data=3))
        bot.send_message(message.chat.id, text="Что вы хотите сделать?", reply_markup=markup)

    #@bot.message_handler(commands=['get_data'])
    #def get_data(message):
    #    markup = telebot.types.InlineKeyboardMarkup()
    #    markup.add(telebot.types.InlineKeyboardButton(text='Получить данные', callback_data=3))
    #    bot.send_message(message.chat.id, text="Что вы хотите сделать?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def query_handler(call):
        answer = ''
        if call.data == '3':
            opc1 = OpenOPC.client()
            opc1.connect("Owen.OPCNet.DA.1")
            #tag1 = opc1.list("COM4.TRM_202(adr=104)T_слой_Ср_р-ра.Оперативные параметры")[3]
            answer = opc1.read(tagsValue, update=1, include_error=True)
            print(answer)
            opc1.close()
            i = 0
            while i < len(tagsValue):
                bot.send_message(call.message.chat.id, "{0:_^20} {1:>10.2f}".format(tg_lst[tagsValue[i]] ,answer[i][1]))
                i += 1

    bot.polling()
###################################################
while True:
    try:
        react_temp = int(input("Введите температуру слоя реактора (целое число): "))
        r_tmp_lim = int(input("Введите допустимое отклонение температур реактора (+- x градусов, целое число): "))
        for_react_temp = int(input("Введите температуру слоя форконтактора (целое число): "))
        fr_tmp_lim = int(input("Введите допустимое отклонение температур форконтактора (+- x градусов, целое число): "))
        prs = float(input("введите давление свд (н-р 20.10): "))
        prs_lim = float(input("введите допустимое отклонение давления свд (н-р 0.05): "))
        poll_time = int(input("Введите частоту опроса, сек (н-р 60, каждые 60 сек. в телеграмм будет отправляться сообщение): "))
    except:
        print("!!!\nВведено некорректное значение\n!!!")
        continue
    if (react_temp and r_tmp_lim and for_react_temp and fr_tmp_lim and prs and prs_lim and poll_time) != None:
        break
    else:
        continue
###################################################
def send_telegram(text: str):
    token = "1203397890:AAF3Z53lbtmCWkXlsxJl4fXRj6Dtcv6TEc0"
    url = "https://api.telegram.org/bot"
    channel_id = "@R8Plant"
    url += token
    method = url + "/sendMessage"

    r = requests.post(method, data={
         "chat_id": channel_id,
         "text": text
          })
    #Print status code - 200 OK
    #print(r.status_code)
    if r.status_code != 200:
        print("Ошибка отправки сообщения в тг")
        #raise Exception("post_text error")
###################################################

# def append_val(tagsValue):
#     try:
#         # Тр-ра Верх
#         tagsValue.append(opc.list("COM4.TRM_202(adr=104)T_слой_Ср_р-ра.Оперативные параметры")[3])
#         # Тр-ра Сер
#         tagsValue.append(opc.list("COM4.TRM_202(adr=112)T_слой_Пр_р-ра.Оперативные параметры")[2])
#         # Тр-ра Низ
#         tagsValue.append(opc.list("COM4.TRM_202(adr=104)T_слой_Ср_р-ра.Оперативные параметры")[2])
#         # Тфр сл
#         tagsValue.append(opc.list("COM4.TRM_202(adr=166)Т_слоя_Ф-К; Т_стенки_Ф-К_ПАЗ.Оперативные параметры")[3])
#
#         # Тр-ра Р_свд
#         tagsValue.append(opc.list("COM4.TRM_202(adr=136)Т_Лев_р-ра_ПАЗ_стенка; P_СВД.Оперативные параметры")[0])
#         # Тр-ра Р_прод
#         tagsValue.append(opc.list("COM4.TRM_202(adr=160)Расход_отдувки.Оперативные параметры")[3])
#     except:
#         print("Не добавить тег")
#     return (tagsValue)

###################################################

def send_mess():
    while True:
        opc = OpenOPC.client()
        servers = opc.servers()
        i = 0
        print("-----------------------------------------------------------------------------------------")
        for serv in servers:
            print(str(i) + " " + serv)
            i += 1
        for srv in servers:
            if (srv == "Owen.OPCNet.DA.1"):
                try:
                    opc.connect(srv)
                    print("-----------------------------------------------------------------------------------------")
                    print("Удачное подключение к " + srv)
                    print("-----------------------------------------------------------------------------------------")
                except:
                    print("не удалось подключиться к " + srv)
                    print("-----------------------------------------------------------------------------------------")
        try:
            ############################################################
            # Проверка температур слоя реактора
            val = opc.read(tagsValue, update=1, include_error=True)
            if int(val[0][1]) > (react_temp + r_tmp_lim) or int(val[1][1]) > (react_temp + r_tmp_lim) or int(
                    val[2][1]) > (react_temp + r_tmp_lim):
                try:
                    # print("here")
                    send_telegram(
                        "Слой реактора перегрет до {0:.2f} {1:.2f} {2:.2f} С".format(val[0][1], val[1][1], val[2][1]))
                except:
                    print("Включите VPN (test 1)")
            if int(val[0][1]) < (react_temp - r_tmp_lim) or int(val[1][1]) < (react_temp - r_tmp_lim) or int(
                    val[2][1]) < (react_temp - r_tmp_lim):
                try:
                    send_telegram(
                        "Слой реактора охладился до {0:.2f} {1:.2f} {2:.2f} С".format(val[0][1], val[1][1], val[2][1]))
                except:
                    print("Включите VPN (test 2)")
            ############################################################
            # Проверка температуры слоя форреактора
            if int(val[3][1]) > (for_react_temp + fr_tmp_lim):
                try:
                    send_telegram("Слой ФР перегрет до {0:.2f} С".format(val[3][1]))
                except:
                    print("Включите VPN (test 3)")
            if int(val[3][1]) < (for_react_temp - fr_tmp_lim):
                try:
                    send_telegram("Слой ФР охладился до {0:.2f} С".format(val[3][1]))
                except:
                    print("Включите VPN (test 4)")
            ############################################################
            # Проверка давления СВД
            if (val[4][1]) > (prs + prs_lim):
                try:
                    send_telegram("Давление поднялось до {0:.2f} ати".format(val[4][1]))
                except:
                    print("Включите VPN (test 5)")
            if (val[4][1]) < (prs - prs_lim):
                try:
                    send_telegram("Давление опустилось до {0:.2f} ати".format(val[4][1]))
                except:
                    print("Включите VPN (test 6)")
            i = 0
            for el in tagsValue:
                print("{} {}".format(el, val[i][1]))
                i += 1

        except:
            raise
            print("error read item")
        opc.close()
        time.sleep(poll_time)

###################################################
# Добавляем теги
# tagsValue = [];
#
# opc = OpenOPC.client()
# servers = opc.servers()
# opc.connect(servers[0])
# append_val(tagsValue)
# opc.close()

file = open(r"C:\Users\user\PycharmProjects\OpcSendPy36-32\tags.txt", "r")
# Получаем словарь из txt-файла. Этот словать нужен для отправки сообщений телеграм
tags = file.read()
tagsValue = tags.split("\n")
tg_lst = {}
for el in tagsValue:
    el = el.split(",")
    tg_lst[el[0]] = el[1]
# print(tagsValue)
# Отрезаем лишнее
# значение после запятой. Получаем теги которые можно считать
i = 0
for el in tagsValue:
    tagsValue[i] = el.split(",")[0]
    i += 1
# print(tagsValue)
file.close()

#send_mess()
thrd_send_mess = threading.Thread(target=send_mess)
thrd_send_mess.start()

thrd_run_setting = threading.Thread(target=run_setting)
thrd_run_setting.start()

