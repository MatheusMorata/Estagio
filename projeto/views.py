from django.shortcuts import render
import requests as r
from datetime import date 

#Função para verificar se uma determinada data é dia util
def dia_util(dia):
    dia = dia.split("-")
    dia_tupla = date(year=int(dia[0]), month=int(dia[1]), day=int(dia[2]))
    n = dia_tupla.weekday()
    if n < 5:
        return True
    else: 
        return False


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
    template = "home.html"
    valores_euro = []
    valores_real = []
    valores_iene = []

    if request.method == "GET":
        data_hoje = date.today()
        dia = data_hoje.day

        for i in range(0,5):
            novo_dia = dia - i
            data = str(data_hoje.year) + "-" + str(data_hoje.month) + "-" + str(novo_dia) #Aqui ele formata a data
            if (novo_dia >= 1 and novo_dia <= 31):
                if (dia_util(data) == True):
                    valores_euro.append(round(cotacao(data)['EUR'],2))
                    valores_real.append(round(cotacao(data)['BRL'],2))
                    valores_iene.append(round(cotacao(data)['JPY'],2))
                else:
                    valores_euro.append(0)
                    valores_real.append(0)
                    valores_iene.append(0)
            else:
                valores_euro.append(0)
                valores_real.append(0)
                valores_iene.append(0)

    #Aqui estou recebendo os dados do formulário
    if request.method == "POST":
        dataInicio = request.POST.get('dataInicio',None)
        dataFim = request.POST.get('dataFim',None)

        dataInicio = dataInicio.split("-")
        dataFim = dataFim.split("-")

        dataInicio = date(year=int(dataInicio[0]), month=int(dataInicio[1]), day=int(dataInicio[2]))
        dataFim = date(year=int(dataFim[0]), month=int(dataFim[1]), day=int(dataFim[2]))
        segundos = (dataFim - dataInicio).total_seconds() #Cálculo da diferença, em segundos, entre os dois dias

        #Diferença menor ou igual a 5 dias.
        if segundos <= 345600:
            j = int(segundos//86400)
            dia = int(dataInicio.day)
            for i in range(0,j+1):
                data = str(dataInicio.year) + "-" + str(dataInicio.month) + "-" + str(dia + i)
                if (dia_util(data) == True):
                    valores_euro.append(round(cotacao(data)['EUR'],2))
                    valores_real.append(round(cotacao(data)['BRL'],2))
                    valores_iene.append(round(cotacao(data)['JPY'],2))
                else:
                    valores_euro.append(0)
                    valores_real.append(0)
                    valores_iene.append(0)
        #Diferença maior que 5 dias.
        else:
            valores_euro = [0,0,0,0,0]
            valores_real = [0,0,0,0,0]
            valores_iene = [0,0,0,0,0]

    c = {'EUR':valores_euro,
        'BRL':valores_real,
        'JPY':valores_iene}

    return render(request,template,c)