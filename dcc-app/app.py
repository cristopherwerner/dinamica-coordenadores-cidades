import json
import re
import time as t
import random
import hashlib

import geocoder as gc
import pandas as pd
import plotly as plt
import plotly.express as px
import pydeck as pdk
import streamlit as st
import streamlit.components.v1 as cp
from unidecode import unidecode

color_palette = [
        [230, 25, 75, 255],    # Vermelho
        [60, 180, 75, 255],    # Verde
        [0, 130, 200, 255],    # Azul
        [245, 130, 48, 255],   # Laranja
        [145, 30, 180, 255],   # Roxo
        [70, 240, 240, 255],   # Ciano
        [240, 50, 230, 255],   # Magenta
        [210, 245, 60, 255],   # Lima
        [250, 190, 190, 255],  # Rosa
        [0, 128, 128, 255],    # Teal
        [230, 190, 255, 255],  # Lavanda
        [170, 110, 40, 255],   # Marrom
        [255, 250, 200, 255],  # Bege
        [128, 0, 0, 255],      # Marrom escuro
        [170, 255, 195, 255],  # Menta
        [128, 128, 0, 255],    # Oliva
        [255, 215, 180, 255],  # Coral
        [0, 0, 128, 255],      # Azul marinho
    ]

def remove_tail(string):
    return string[:-8]

def format():
    with open('latlonCidades.json', 'r', encoding='utf-8') as f:
        str_data = f.read()

    str_data_decoded = bytes(str_data, 'utf-8').decode('unicode_escape')

    jsonfixed = json.loads(str_data_decoded)

    for city in jsonfixed:
        for key, value in city.items():
            if isinstance(value, str):
                city[key] = unidecode(value)

    with open('latlonCidades.json', 'w', encoding='utf-8') as f:
        json.dump(jsonfixed, f, ensure_ascii=False, indent=4)

def update_latlonjson():
    latlonCidades = []

    with open('latlonCidades.json', 'w', encoding='utf-8') as of:
        for i in range(len(cidadeUF)):
        # # # # # # # # GET LAT AND LNG FROM ADDRESSES FOR MAP CREATION # # # # # # # # #
            latlonCidades.append(gc.bing(cidadeUF[i],
                                        key='Arvd_e7iYj5u2z0LLK17t-u6WZ0Y5AUs-R10tUKKSpaGtmehLTiMzRmPgXF-Fwq2').json
                                )
        
        json.dump(latlonCidades, of,indent=4, ensure_ascii='False')

    format()

def coord_colors(coords):
    colors = {}

    for i, c in enumerate(coords):
        colors[c] = color_palette[i % len(color_palette)]

    return colors


# def hash_to_color(name):
    name_hash = hashlib.sha256(name.encode()).hexdigest()
    name_num = int(name_hash, 16) / float(1 << 256)

    return [int(255*name_num), 
            int(255*(1-name_num)), 
            (255-int(255*name_num)-int(255*(1-name_num))), 
            255]

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

title_question = st.empty()
upt_dados = st.empty()
upt_status = st.empty

with title_question:
    st.markdown(text0MD, unsafe_allow_html=True)
    # UPDATE CITIES LAT LON AND FORMAT CITY NAMES

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

        if nao:
            title_question.empty()
            upt_dados.empty()
            

# update_latlonjson()

with open('latlonCidades.json', 'r') as of:
    jsonfile = json.load(of)


procData = []
for item in jsonfile:
    city = remove_tail(item['address'])
    lat = item['lat']
    lng = item['lng']
    procData.append({'Cidade':city, 'lat':lat, 'lng':lng})

df_jsonfile = pd.DataFrame(procData)

for i, row in df_coordenadores_cidades.iterrows():
    df_coordenadores_cidades = df_coordenadores_cidades.loc[:,~df_coordenadores_cidades.columns.duplicated()]
    cidade = row['CidadeNormalizada']

    match = df_jsonfile[df_jsonfile['Cidade'] == cidade]

    if not match.empty:
        df_coordenadores_cidades.at[i, 'LAT'] = match['lat'].values[0]
        df_coordenadores_cidades.at[i, 'LON'] = match['lng'].values[0]


st.title('Dinamica Merchandising')

col1, col2 = st.columns([1.5, 2])

with st.container():
    st.subheader("Dados dos Coordenadores")
    st.table(df_coordenadores)

with st.container():
    st.subheader("Coordenadores e Cidades")
    df_coor_cid = df_coordenadores_cidades.drop(labels='Cidade', axis=1)
    df_coor_cid.rename(columns={"CidadeNormalizada": "Cidade"}, inplace=True)
    # HIDDING TABLES #
    # st.table(df_coor_cid)
    # st.write(df_coor_cid.value_counts(['Coordenador']))
    # st.write(cidadeUF)
    numCoord = df_coor_cid['Coordenador'].nunique()
    coords = df_coor_cid['Coordenador'].unique()
    coordcol = coord_colors(coords)
    df_coor_cid['color'] = df_coor_cid['Coordenador'].map(coordcol)
    df_coor_cid = df_coor_cid.dropna()
    st.write(df_coor_cid)

    
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
                        radius = 20,
                        center = dict(lat=0, lon=180),
                        zoom = 3,
                        mapbox_style = "stamen-terrain"
                    )
    
    st.markdown("### Legenda")
    for coordenador, cor in coordcol.items():
        cor_rgb = 'rgba({},{},{},{})'.format(*cor)
        st.markdown(f"<div style='display: inline-block; height: 24px; width: 24px; background-color: {cor_rgb}'></div> {coordenador}", unsafe_allow_html=True)


    layer = pdk.Layer(
        "ScatterplotLayer",
        data = df_coor_cid,
        get_position = ['LON', 'LAT'],
        get_fill_color = 'color',
        get_radius = 5000,
    )

    view_state = pdk.ViewState(latitude=df_coor_cid['LAT'].mean(), longitude=df_coor_cid['LON'].mean(), zoom=6)

    pydeckD = pdk.Deck(layers=[layer], initial_view_state=view_state)

    st.pydeck_chart(pydeckD)
    
    map.update_layout(mapbox_style="open-street-map")
    map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    st.plotly_chart(map)
    st.plotly_chart(hmap)

with st.container():
    st.subheader("Coordenadores e Cidades")
    