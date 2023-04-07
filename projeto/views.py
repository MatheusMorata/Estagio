from django.shortcuts import render
import requests as r
from datetime import date 
from django.views.decorators.csrf import csrf_exempt



#Função que verifica quantos dias tem um determinado mês
def dias_mes(mes,ano):
    # Meses com 31 dias
    if mes in [1,3,5,7,8,10,12]:
            return 1
    # Meses com 30 dias
    elif mes in [4,6,9,11]:
            return 2
    elif mes==2:
        # Testa se é bissexto
        if (ano%4==0 and ano%100!=0) or (ano%400==0):
            return 3
        else:
            return 4
        
#Função para verificar se uma determinada data é dia util
def dia_util(dia):
    dia = dia.split("-")
    dia_tupla = date(year=int(dia[0]), month=int(dia[1]), day=int(dia[2]))
    n = dia_tupla.weekday()
    if n < 5:
        return True
    else: 
        return False

#Função que faz a requisição na API 
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

@csrf_exempt
def home(request):
    template = "home.html"
    cotacoes_dias = []
    valores_euro = []
    valores_real = []
    valores_iene = []

    #Quando o usuário acessa a página pela 1° vez 
    if request.method == "GET":
        dias_uteis = []
        data_hoje = date.today()
        dia = data_hoje.day
        mes = data_hoje.month

        while (len(dias_uteis) < 5):  
            data = str(data_hoje.year) + "-" + str(mes) + "-" + str(dia)
            if(dia == 0):
                mes = int(data_hoje.month - 1)
                if(dias_mes(mes,int(data_hoje.year)) == 1):
                    dia = 31
                    data = str(data_hoje.year) + "-" + str(mes) + "-" + str(dia)
                elif(dias_mes(mes,int(data_hoje.year)) == 2):
                    dia = 30
                    data = str(data_hoje.year) + "-" + str(mes) + "-" + str(dia)
                elif(dias_mes(mes,int(data_hoje.year)) == 3):
                    dia = 29
                    data = str(data_hoje.year) + "-" + str(mes) + "-" + str(dia)
                else:
                    dia = 28
                    data = str(data_hoje.year) + "-" + str(mes) + "-" + str(dia)
            if(dia_util(data) == True):
                dias_uteis.append(data)
            dia = dia - 1
            
        for i in range(0,5):
            cotacoes_dias.append(dias_uteis[i])
            valores_euro.append(round(cotacao(dias_uteis[i])['EUR'],2))
            valores_real.append(round(cotacao(dias_uteis[i])['BRL'],2))
            valores_iene.append(round(cotacao(dias_uteis[i])['JPY'],2))

        cotacoes_dias.reverse()
        valores_euro.reverse()
        valores_real.reverse()
        valores_iene.reverse()

    #Aqui estou recebendo os dados do formulário
    if request.method == "POST":
        dataInicio = request.POST.get('dataInicio',None)
        dataFim = request.POST.get('dataFim',None)

        dataInicio = dataInicio.split("-")
        dataFim = dataFim.split("-")

        dataInicio = date(year=int(dataInicio[0]), month=int(dataInicio[1]), day=int(dataInicio[2]))
        dataFim = date(year=int(dataFim[0]), month=int(dataFim[1]), day=int(dataFim[2]))
        segundos = (dataFim - dataInicio).total_seconds() #Cálculo da diferença, em segundos, entre os dois dias

        #Diferença menor ou igual a 5 dias uteis.
        if segundos <= 518400:
            j = int(segundos//86400)
            dia = int(dataInicio.day)
            novo_dia = dia 
            for i in range(0,j+1):
                if(dias_mes(int(dataInicio.month),int(dataInicio.year)) == 1): #Mês com 31 dias
                    if(novo_dia == 32):
                        novo_dia = 1
                        mes_novo = int(dataInicio.month + 1)
                        dataInicio = date(year=int(dataInicio.year), month=mes_novo, day=novo_dia) 
                elif(dias_mes(int(dataInicio.month),int(dataInicio.year)) == 2): #Mês com 30 dias
                    if(novo_dia == 31):
                        novo_dia = 1
                        mes_novo = int(dataInicio.month + 1)
                        dataInicio = date(year=int(dataInicio.year), month=mes_novo, day=novo_dia) 
                elif(dias_mes(int(dataInicio.month),int(dataInicio.year))): #Mês com 28 dias
                    if(novo_dia == 30):
                        novo_dia = 1
                        mes_novo = int(dataInicio.month + 1) 
                        dataInicio = date(year=int(dataInicio.year), month=mes_novo, day=novo_dia) 
                else: #Mês com 29 dias
                    if(novo_dia == 29):
                        novo_dia = 1
                        mes_novo = int(dataInicio.month + 1) 
                        dataInicio = date(year=int(dataInicio.year), month=mes_novo, day=novo_dia) 
                data = str(dataInicio.year) + "-" + str(dataInicio.month) + "-" + str(novo_dia)
                if (dia_util(data) == True):
                    cotacoes_dias.append(data)
                    valores_euro.append(round(cotacao(data)['EUR'],2))
                    valores_real.append(round(cotacao(data)['BRL'],2))
                    valores_iene.append(round(cotacao(data)['JPY'],2))
                novo_dia = novo_dia + 1
        #Diferença maior que 5 dias.
        else:
            valores_euro = []
            valores_real = []
            valores_iene = []

    c = {'EUR':valores_euro,
        'BRL':valores_real,
        'JPY':valores_iene,
        'dias':cotacoes_dias}

    return render(request,template,c)