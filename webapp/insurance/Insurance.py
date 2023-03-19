# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 08:55:39 2023

@author: alanc
"""

import pickle
import inflection
import pandas as pd
import numpy as np
import math

## DATA CLEANING + FEATURE ENGINEERING + DATA FILTERING + DATA PREPARATION + FEATURE SELECTION

class PropensityScore( object ):
    def __init__( self ):
        self.home_path             = ''
        self.age_scaler            = pickle.load(open(self.home_path + 'parameters/age_scaler.pkl', 'rb'))
        self.annual_premium_scaler = pickle.load(open(self.home_path + 'parameters/annual_premium_scaler.pkl', 'rb'))
        self.days_client_scaler    = pickle.load(open(self.home_path + 'parameters/days_client_scaler.pkl', 'rb'))
        self.region_channel_enc    = pickle.load(open(self.home_path + 'parameters/region_code_sales_channel_target.pkl', 'rb'))
        self.features_one_hot_enc  = pickle.load(open(self.home_path + 'parameters/features_one_hot.pkl', 'rb'))


    def data_cleaning(self, df1):

        ## 1.1. Rename Columns ---------------------------------------------------------------------

        cols_origin = df1.columns.tolist()

        ## Utiliza função lambda encapsulada para transformar para snake_case os atributos
        snakecase = lambda x: inflection.underscore( x )

        ## Map - Mapeia cada valor dentro da estrutura de dado passada e aplica a função snakecase
        cols_new = list( map( snakecase, cols_origin ) )

        ## underscore columns
        df1.columns = cols_new

        ## rename columns
        df1.rename(columns = {'policy_sales_channel':'sales_channel', 'previously_insured' : 'vehicle_insured',
                              'vintage': 'days_client_associate'}, inplace = True)

        ## 1.3. Data Types ---------------------------------------------------------------------

        df1['region_code'] = df1['region_code'].astype('int64')
        df1['sales_channel'] = df1['sales_channel'].astype('int64')


        return df1


    def feature_engineering(self, df2):

        ## FEATURE ENGINEERING + DATA FILTERING

        ## 2.4. Feature Engineering

        # gender   [Male, Female] -> [ Masculino, Feminino ]

        df2.replace( {'gender': {'Male':'Masculino', 'Female': 'Feminino'}}, inplace = True )

        # driving_license     [1, 0]

        df2['driving_license'] = df2['driving_license'].apply(lambda x: 'Possui carteira' if x == 1 else 'Sem carteira')

        # vehicle_age      [> 2 Years, 1-2 Year, < 1 Year]

        df2['vehicle_age'] = df2['vehicle_age'].apply(lambda x: 'Menos de 1 ano' if x == '< 1 Year' else 'Entre 1 e 2 anos' if x == '1-2 Year' else
                                                    'Mais de 2 anos')

        # vehicle_damage  [Yes, No]

        df2['vehicle_damage'] = df2['vehicle_damage'].apply(lambda x: 'Foi danificado' if x == 'Yes' else 'Não foi danificado')

        # vehicle_insured  [0, 1]

        df2['vehicle_insured'] = df2['vehicle_insured'].apply(lambda x: 'Já possui seguro' if x == 1 else 'Não possui seguro')


        ### Das variáveis -> SEPARAR EM VARIÁVEIS CATEGÓRICAS QUANTITATIVAS


        # age -> [20-30 | 31-50 | 51 - 80]

        df2['age_level'] = df2['age'].apply(lambda x: '20-30' if (x >= 20) & (x <= 30) else '31-40' if (x > 30) & (x <= 40) else '41-50'
                                                              if (x > 40) & (x <= 50) else '51-85')

        # days_client_associate -> [ 10-100 | 101-200 | 201-299 ]

        df2['days_client_associate_level'] = df2['days_client_associate'].apply(lambda x: '10-100' if (x >= 10) & (x <= 100) else '101-200' if (x > 100) & (x <= 200) else '201-299' )


        # annual_premium -> Range grande que vai de 2.630,00 a 540.165,00


        df2["annual_premium_level"] = df2["annual_premium"].apply(lambda x: '0-20000' if (x >= 0) & (x <= 20000) else '20001-25000'
                                                                                      if (x > 20000) & (x <= 25000) else '25001-30000'
                                                                                      if (x > 25000) & (x <= 30000) else '30001-35000'
                                                                                      if (x > 30000) & (x <= 35000) else '35001-40000'
                                                                                      if (x > 35000) & (x <= 40000) else '40001-60000'
                                                                                      if (x > 40000) & (x <= 60000) else '60001-540165')


        # 3.0. FILTRAGEM DE VARIÁVEIS

        # No feature filtering was done

        return df2

    def data_preparation(self, df3):

        ## 5.1 Normalization

        df3['days_client_associate'] = self.days_client_scaler.transform( df3[['days_client_associate']].values )

        ## 5.2. Rescaling

        df3['age'] = self.age_scaler.transform( df3[['age']].values )

        df3['annual_premium'] = self.annual_premium_scaler.transform( df3[['annual_premium']].values )

        ## 5.3 Encoding

        # # Variáveis Ordinais:

        ########### vehicle_age - Ordinal Encoding

        vehicle_age_dict = {'Menos de 1 ano': 0 , 'Entre 1 e 2 anos': 1, 'Mais de 2 anos': 2}

        df3['vehicle_age'] = df3['vehicle_age'].map( vehicle_age_dict )

        ########## age_level - Ordinal Encoding

        age_level_dict = {'20-30': 0 , '31-40': 1, '41-50': 2, '51-85': 3}

        df3['age_level'] = df3['age_level'].map( age_level_dict )

        ######### days_client_associate_level - Ordinal Encoding

        dcal_dict = {'10-100': 0 , '101-200': 1, '201-299' : 2}

        df3['days_client_associate_level'] = df3['days_client_associate_level'].map( dcal_dict )

        ######### annual_premium_level - Ordinal Encoding

        apl_dict = {'0-20000': 0 , '20001-25000': 1, '25001-30000': 2, '30001-35000': 3,'35001-40000': 4, '40001-60000': 5,
                    '60001-540165': 6}

        df3['annual_premium_level'] = df3['annual_premium_level'].map( apl_dict )


        # Variáveis Nominais:

        ######### region_code e sales_channel - Target Encoding

        ## transformando em object
        df3[['region_code', 'sales_channel']] = df3[['region_code', 'sales_channel']].astype("object")

        df3 = self.region_channel_enc.transform(df3)


        ############ 'driving_license', 'vehicle_damage', 'vehicle_insured', 'gender' - One Hot Encoding

        # arrumar nome das categorias, tirar espaços
        df3.replace( {'driving_license': {'Possui carteira': 'yes','Sem carteira': 'no'},
                          'vehicle_damage': {'Foi danificado': 'yes','Não foi danificado': 'no'},
                          'vehicle_insured': {'Já possui seguro': 'yes','Não possui seguro': 'no'}}, inplace = True )


        df3 = self.features_one_hot_enc.transform(df3)
        df3 = pd.DataFrame(df3, columns=self.features_one_hot_enc.get_feature_names_out())

        # Feature Selection
        cols_selected = ['remainder__age','remainder__age_level','remainder__annual_premium','remainder__annual_premium_level',
                         'remainder__days_client_associate','remainder__days_client_associate_level','onehotencoder__driving_license_no',
                         'onehotencoder__driving_license_yes','remainder__region_code','remainder__sales_channel','remainder__vehicle_age',
                         'onehotencoder__vehicle_damage_no','onehotencoder__vehicle_damage_yes','onehotencoder__vehicle_insured_no',
                         'onehotencoder__vehicle_insured_yes']

        return df3[cols_selected]


    def get_ranking(self, model,  prod_raw, prod_trans ):

        # Probabilies of classes
        prob_class = model.predict_proba( prod_trans )

        # Propensão de Score de interessados predito pelo modelo
        prod_raw["prop_score"] = prob_class[ : , 1 ].tolist()

        # Ordenação da lista pela probabilidade das amostras serem da classe 1 - Interessado
        prod_raw = prod_raw.sort_values( by = 'prop_score', ascending = False ).reset_index(drop = True)

        return prod_raw.to_json( orient = 'records', date_format = 'iso' )
