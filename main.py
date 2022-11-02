from email import header
from typing import Tuple, Type
import requests
from bs4 import BeautifulSoup
import locale
import pandas as pd
import numpy as np
from modelos import Estrategia, FundoImobiliario


locale.setlocale(locale.LC_ALL,'pt_BR.UTF-8')

def trata_porcentagem(percent_str):
    """Essa função recebe um valor em string e faz o tratamento para floate retirando o % da string_

    Args:
        percent_str (valor): em formato string

    Returns:
        float: número sem o %_
    """    
    return locale.atof(percent_str.split('%')[0])

def trata_decimal(decimal_str):
    """Essa função recebe um valor em string e faz o tratamento para decimal retirando o R$ da string_

    Args:
        decimal_str (valor): em formato string

    Returns:
        float: número sem o R$_    """ 
    
    return locale.atof(decimal_str)


# Requisição site fundamentus
# O site espera que a requisição venha de um browser , por isso utilizar o header abaixo
header = {'User-Agent' : 'Mozilla/5.0'}

requisicao = requests.get('https://www.fundamentus.com.br/fii_resultado.php',headers=header)

if requisicao.status_code == 200:
    print('Requisição bem sucedida.')

else:
    print(requisicao.status_code,requisicao.text)

# Realizando o parser da requisição com o beautifulsoup
soup = BeautifulSoup(requisicao.text,'html.parser')

# Find no id da tabela
tabela = soup.find(id='tabelaResultado')

# Find na t-body
body = tabela.find('tbody')

# Findall em todas as linhas da tabela
linhas = body.find_all('tr')

# Iterando as linhas para capturar todas as informações
resultado = [] # lista que recebe os valores após a aplicação das estratégias

# Definindo a estrategia que será utilizada na captura dos dados
estrategia = Estrategia(
    cotacao_atual_minima=0.0,
    dividend_yield=0,
    p_vp_minimo=0.0,
    valor_mercado_minimo=0,
    liquidez_minima=0,
    qt_minima_imoveis=1,
    maxima_vacancia_media=0
)

for linha in linhas:
    dados = linha.find_all('td')
    codigo = dados[0].text
    segmento = dados[1].text
    cotacao = trata_decimal(dados[2].text)
    ffo_yield = trata_porcentagem(dados[3].text)
    dividend_yield = trata_porcentagem(dados[4].text)
    p_vp = trata_decimal(dados[5].text)
    valor_mercado = trata_decimal(dados[6].text)
    liquidez = trata_decimal(dados[7].text)
    qt_imoveis = int(dados[8].text)
    preco_m2 = trata_decimal(dados[9].text)
    aluguel_m2 = trata_decimal(dados[10].text)
    cap_rate = trata_porcentagem(dados[11].text)
    vacancia = trata_porcentagem(dados[12].text)
    


    fundo_imobiliario = FundoImobiliario(codigo,segmento,cotacao,ffo_yield,dividend_yield,p_vp,valor_mercado,liquidez,
    qt_imoveis,preco_m2,aluguel_m2,cap_rate,vacancia)

    # Aplicando a estrategia definida nos dados coletados e adcionando a lista resultado
    if estrategia.aplica_estrategia(fundo_imobiliario):
        resultado.append(fundo_imobiliario)

# Criação do dataframe utilizando a biblioteca pandas

cabecalho = ["CÓDIGO","SEGMENTO","COTAÇÃO ATUAL","DIVIDEND YIELD"]
tabela = []

for elemento in resultado:
    tabela.append([
            elemento.codigo,elemento.segmento,elemento.cotacao_atual,elemento.dividend_yield
        ]
    )

df = pd.DataFrame(np.array(tabela),columns=cabecalho)


