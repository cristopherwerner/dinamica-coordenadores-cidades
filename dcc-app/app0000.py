# import googlesheets
import json
import re
import time as t
import geocoder as gc
import pandas as pd
import plotly as plt
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as cp
from unidecode import unidecode


global progress_try
progress_try = 0
global total_iter
total_iter = 0
global pbarP
pbarP = st.empty()

def remove_tail(string):
    return string[:-8]

def format():
    with open('latlonCidades.json', 'r', encoding='utf-8') as f:
        str_data = f.read()

    str_data_decoded = bytes(str_data, 'utf-8').decode('unicode_escape')

    jsonfixed = json.loads(str_data_decoded)

    i = 1
    totalcity = len(jsonfixed)

    for city in jsonfixed:
        pbarP.progress(value=i/totalcity,text="Formatando Arquivo JSON...")
        for key, value in city.items():
            if isinstance(value, str):
                city[key] = unidecode(value)

    with open('latlonCidades.json', 'w', encoding='utf-8') as f:
        json.dump(jsonfixed, f, ensure_ascii=False, indent=4)
    pbarP.empty()

def update_latlonjson():
    latlonCidades = []

    with open('latlonCidades.json', 'w', encoding='utf-8') as of:
        for i in range(len(cidadeUF)):
            pbarP.progress(value=i/len(cidadeUF), text="Padronizando Dados...")
        # # # # # # # # GET LAT AND LNG FROM ADDRESSES FOR MAP CREATION # # # # # # # # #
            latlonCidades.append(gc.bing(cidadeUF[i],
                                        key='Arvd_e7iYj5u2z0LLK17t-u6WZ0Y5AUs-R10tUKKSpaGtmehLTiMzRmPgXF-Fwq2').json
                                )
        
        json.dump(latlonCidades, of,indent=4, ensure_ascii='False')

text0MD = '<p align="center" style="color:lightblue; font-size:30px;">Atualizar os dados das cidades?</p>'
text1MD = '<p align="center" style="color:green; font-size:40px;">Dados Atualizados!</p>'

df_sheets = pd.ExcelFile('DCM.xlsm')
df_coordenadores = pd.read_excel(df_sheets, 'Coordenador')
df_coordenadores_cidades = pd.read_excel(df_sheets, 'CoordenadorCidade')
cidadeUF = []
cidadeUF = (df_coordenadores_cidades['CidadeNormalizada'].astype(str) + 
            ', ' + 
            df_coordenadores_cidades['Estado'].astype(str)
)

global title_question
title_question = st.empty()
global upt_dados
upt_dados = st.empty()
global upt_status
upt_status = st.empty

# MENU FOR UPDATING OR NOT THE DATA ABOUT THE MAIN TABLE CITIES #
def updateScreen():
    global jsonfile
    with title_question:
        st.markdown(text0MD, unsafe_allow_html=True)
        with upt_dados:
            
            c0, c1, c2, c3, c4 = st.columns(5)
            with c1:
                sim = st.button('Sim')
            with c4:
                nao = st.button('Não')
            if sim:
                title_question.empty()
                update_latlonjson()
                title_question.empty()
                title_question.markdown(text1MD, unsafe_allow_html=True)
                t.sleep(3)
                title_question.empty()
                with open('latlonCidades.json', 'r') as of:
                    jsonfile = json.load(of)

            if nao:
                title_question.empty()
                upt_dados.empty()
                with open('latlonCidades.json', 'r') as of:
                    jsonfile = json.load(of)
    jsonProcessing(jsonfile)
                


# PROCESS JSON DATA INTO PANDAS DATAFRAME AND CALLS cityCoordUpdate()#
def jsonProcessing(jsonfile):
    procData = []
    for item in jsonfile:
        city = remove_tail(item['address'])
        lat = item['lat']
        lng = item['lng']
        procData.append({'Cidade':city, 'lat':lat, 'lng':lng})

    df_jsonfile = pd.DataFrame(procData)

    cityCoordUpdate(df_jsonfile)


# UPDATE CITIES LAT AND LNG DATA ON MAIN TABLE # 
def cityCoordUpdate(df_jsonfile):
    for i, row in df_coordenadores_cidades.iterrows():
        df_coordenadores_cidades = df_coordenadores_cidades.loc[:,~df_coordenadores_cidades.columns.duplicated()]
        cidade = row['CidadeNormalizada']

        match = df_jsonfile[df_jsonfile['Cidade'] == cidade]

        if not match.empty:
            df_coordenadores_cidades.at[i, 'LAT'] = match['lat'].values[0]
            df_coordenadores_cidades.at[i, 'LON'] = match['lng'].values[0]
    Dash()

def Dash():
    st.title('Dinamica Merchandising')

    col1, col2 = st.columns([1.5, 2])

    with st.container():
        st.subheader("Dados dos Coordenadores")
        st.table(df_coordenadores)

    with st.container():
        st.subheader("Coordenadores e Cidades")
        df_coor_cid = df_coordenadores_cidades.drop(labels='Cidade', axis=1)
        df_coor_cid.rename(columns={"CidadeNormalizada": "Cidade"}, inplace=True)
        st.table(df_coor_cid)
        st.write(df_coor_cid.value_counts(['Coordenador']))
        st.write(cidadeUF)
        
        map = px.scatter_mapbox(df_coor_cid,
                            lat = 'LAT',
                            lon = 'LON',
                            hover_name = 'Coordenador',
                            zoom = 3
                        )
        
        hmap = px.density_mapbox(df_coor_cid,
                            lat = 'LAT',
                            lon = 'LON',
                            z = 'Coordenador',
                            radius = 10,
                            center = dict(lat=0, lon=180),
                            zoom = 3,
                            mapbox_style = "stamen-terrain"
                        )
        
        map.update_layout(mapbox_style="open-street-map")
        map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
        st.plotly_chart(map)
        st.plotly_chart(hmap)

    with st.container():
        st.subheader("Coordenadores e Cidades")
    
updateScreen()