from django.shortcuts import render
import requests as r
import datetime 


def cotacao(data):
    url = "https://api.vatcomply.com/rates?date=" + data #URL da requisição
    resultado = r.get(url) #Método GET
    json = resultado.json()

    EUR = 1/float(json['rates']['USD'])
    BRL = float(json['rates']['BRL'])/float(json['rates']['USD'])
    JPY = float(json['rates']['JPY'])/float(json['rates']['USD'])

    json = {'EUR':EUR,
            'BRL':BRL,
            'JPY':JPY}
    return json

    
def home(request):
    data_hoje = datetime.datetime.now()#Aqui ela captura a data de hoje

    valores_euro = []
    valores_real = []
    valores_iene = []
    d = []

    for i in range(0,5):
        dia = data_hoje.day - i
        if (dia >= 1) and (dia <= 31):
            data = str(data_hoje.year) + "-" + str(data_hoje.month) + "-" + str(dia) #Aqui ele formata a data que vai ser usada na requisição
            d.append(data)
            valores_euro.append(round(cotacao(data)['EUR'],2))
            valores_real.append(round(cotacao(data)['BRL'],2))
            valores_iene.append(round(cotacao(data)['JPY'],2))


    c = {'EUR':valores_euro,
        'BRL':valores_real,
        'JPY':valores_iene,
        'datas':d}

    return render(request,"home.html",c)