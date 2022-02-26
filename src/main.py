from itertools import groupby
from operator import itemgetter
from flask import Flask, request
from flask_restx import Api, Resource, reqparse
import datetime


app = Flask(__name__)
api = Api(app)
app.config["DEBUG"] = True

metas_db = [
{'mes' : 1, 'qtd' : 5},
{'mes' : 2, 'qtd' : 3},
{'mes' : 3, 'qtd' : 2},
{'mes' : 4, 'qtd' : 2},
{'mes' : 5, 'qtd' : 5},
{'mes' : 6, 'qtd' : 60},
{'mes' : 8, 'qtd' : 2},
{'mes' : 9, 'qtd' : 4},
{'mes' : 10, 'qtd' : 4},
{'mes' : 11, 'qtd' : 7},
{'mes' : 12, 'qtd' : 2}
]

def formata_data(data):
    format = '%Y-%m-%d'
    date = datetime.datetime.strptime(data, format)
    date = date.month
    return date

def calcula_comissao(valor):
    calc = 0.00
    if (valor <= 300):
        calc = valor*0.01
    if (valor > 300 ):
        if (valor <= 1000):
            calc = valor*0.03
    if (valor > 1000):
        calc = valor*0.05
    return calc


def preprocessamento(response):
    dics = response['pedidos']
    dics.sort(key=itemgetter("vendedor"))
    result = {}
    resultf = []
    for vendedor, group in groupby(dics, key=itemgetter("vendedor")):
        result[vendedor] = list(group)
    for vendedor, lista in result.items():
        lista.sort(key=lambda x:x['data'][:7])
        for k,v in groupby(lista,key=lambda x:x['data'][:7]):
            lista = list(v)
            cria_resposta(lista, resultf)
    comissoes = {"comissoes": resultf}
    return comissoes

def cria_resposta(lista, result):
    vendedor = lista[0]["vendedor"]
    data = lista[0]["data"]
    date = formata_data(data)
    comissao = 0.00
    valor = 0.00
    qtd_vendas = 0
    for index in range(len(lista)):
        qtd_vendas = qtd_vendas+1
        valor = valor + lista[index]['valor']
        comissao = comissao + calcula_comissao(lista[index]['valor'])
    for index in range(len(metas_db)):
        if (metas_db[index]['mes'] == date and metas_db[index]['qtd'] <= qtd_vendas):
            comissao = comissao + valor*0.03
    venda_mensal = {'vendedor' : vendedor, 'mes' : date, 'valor': round(comissao, 2) }
    result.append(venda_mensal)

    

@api.route('/calcula-comissao')
class ComissionList(Resource):
    def post(self, ):
        response = request.get_json('pedidos')
        return preprocessamento(response)


app.run()