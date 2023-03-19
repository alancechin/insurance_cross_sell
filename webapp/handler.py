# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 08:58:11 2023

@author: alanc
"""

import pandas as pd
import os
import pickle


## Importando classe PropensityScore do arquivo Insurance.py da pasta insurance

#from nome_pasta.nome_arquivo import class_in_arquivo
from insurance.Insurance import PropensityScore


## Biblioteca para construir interfaces(app) Web em Python para construir API´s
from flask import Flask, request, Response

# loading model
model = pickle.load(open('model/model_lgbm.pkl', 'rb'))

# instaciando objeto da classe Flask que será a API
app = Flask( __name__ )

# criando endpoint com método POST (envia algum dado para poder receber)
## método GET (pede algum dado para poder receber)
@app.route('/insurance/ranking', methods = ['POST']) # roda a primeira função que estiver embaixo dele
def insurance_ranking():
    prod_json = request.get_json() ## Classe request com método get_json() para puxar o dado enviado para a API

    if prod_json: # Para checar se há dado
        if isinstance(prod_json, dict): #unique example/observations/sample in dict
            prod_raw = pd.DataFrame(prod_json, index = [0])

        else: #multiple example/observations/sample in dict (dict aninhado)
            prod_raw = pd.DataFrame(prod_json, columns = prod_json[0].keys() )


        raw = prod_raw.copy()

        ## Intanciando objeto da classe PropensityScore
        ps = PropensityScore()

        # data cleaning - começo a usar os métodos da classe FeatureTransformation criada
        df1 = ps.data_cleaning( raw )

        # feature engineering
        df2 = ps.feature_engineering( df1 )

        # data preparation
        prod_trans = ps.data_preparation( df2 )

        # learnrank
        df_response = ps.get_ranking(model, prod_raw, prod_trans)

        return df_response ## Dado resposta para a entidade que solitou algo via dado


    else: ## Resposta se não tiver dado, ou seja, vazio

        return Response( '{}', status = 200, mimetype = 'application/json')

if __name__ == '__main__':## interpretador python irá procurar essa função ao rodar o script
    port = os.environ.get('PORT', 5000)
    app.run( host = '0.0.0.0', port = port )

    #app.run( '192.168.0.7') #, debug=True) ## dizer para endpoint rodar no localhost (rodando na máquina)
# 192.168.0.7 -> endereço IPv4 pc local
