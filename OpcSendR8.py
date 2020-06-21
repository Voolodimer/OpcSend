# -*- coding: utf-8 -*-
import OpenOPC
import time
import requests

###################################################
try:
    react_temp = int(input("Введите температуру слоя реактора (целое число): "))
    r_tmp_lim = int(input("Введите допустимое отклонение температур реактора (+- x градусов, целое число): "))
    for_react_temp = int(input("Введите температуру слоя форконтактора (целое число): "))
    fr_tmp_lim = int(input("Введите допустимое отклонение температур форконтактора (+- x градусов, целое число): "))
    prs = float(input("введите давление свд (н-р 20.10): "))
    prs_lim = float(input("введите допустимое отклонение давления свд (н-р 0.05): "))
    poll_time = int(input("Введите частоту опроса, сек (н-р 60, каждую минуту в телеграмм будет отправляться сообщение о сотоянии): "))
except:
    print("Введено неверное значение")
###################################################
def send_telegram(text: str):
    token = "1203397890:AAFupM7Z1QXBuTOdDI2lwgpPwmYYAgX0p4o"
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
        raise Exception("post_text error")
###################################################

def append_val(tagsValue):
    try:
        # Тр-ра Верх
        tagsValue.append(opc.list("COM4.TRM_202(adr=104)T_слой_Ср_р-ра.Оперативные параметры")[3])
        # Тр-ра Сер
        tagsValue.append(opc.list("COM4.TRM_202(adr=112)T_слой_Пр_р-ра.Оперативные параметры")[2])
        # Тр-ра Низ
        tagsValue.append(opc.list("COM4.TRM_202(adr=104)T_слой_Ср_р-ра.Оперативные параметры")[2])
        # Тфр сл
        tagsValue.append(opc.list("COM4.TRM_202(adr=166)Т_слоя_Ф-К; Т_стенки_Ф-К_ПАЗ.Оперативные параметры")[3])

        # Тр-ра Р_свд
        tagsValue.append(opc.list("COM4.TRM_202(adr=136)Т_Лев_р-ра_ПАЗ_стенка; P_СВД.Оперативные параметры")[0])
        # Тр-ра Р_прод
        tagsValue.append(opc.list("COM4.TRM_202(adr=160)Расход_отдувки.Оперативные параметры")[3])
    except:
        print("Не добавить тег")
    return (tagsValue)

###################################################

opc = OpenOPC.client()
servers = opc.servers()
#print(servers)
try:
    opc.connect("Owen.OPCNet.DA.1")
    print("-----------------------------------------------------------------------------------------")
    print("Удачное подключение к " + servers[0])
except:
    print("не удалось подключиться к ОРС - серверу")
#list_par = opc.list('COM4.*.Оперативные параметры')

#for elem in list_par:
#    print(elem)
#--------------------------------------------------------------------------------------------------------#
tagsValue = [];
append_val(tagsValue)
#print(opc.list('COM4.TRM_202(adr=112)T_слой_Пр_р-ра'))

while True:
    print("-----------------------------------------------------------------------------------------")
    try:
        ############################################################
        # Проверка температур слоя реактора
        val = opc.read(tagsValue, update=1, include_error=True)
        if int(val[0][1]) > (react_temp + r_tmp_lim) or int(val[1][1]) > (react_temp + r_tmp_lim) or int(val[2][1]) > (react_temp + r_tmp_lim):
            try:
                #print("here")
                send_telegram("Слой реактора перегрет до {0:.2f} {1:.2f} {2:.2f} С".format(val[0][1], val[1][1], val[2][1]))
            except:
                print("Включите VPN (test 1)")
        if int(val[0][1]) < (react_temp - r_tmp_lim) or int(val[1][1]) < (react_temp - r_tmp_lim) or int(val[2][1]) < (react_temp - r_tmp_lim):
            try:
                send_telegram("Слой реактора охладился до {0:.2f} {1:.2f} {2:.2f} С".format(val[0][1], val[1][1], val[2][1]))
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
        print("error read item")
    time.sleep(poll_time)

opc.close()
#---------------------------#
