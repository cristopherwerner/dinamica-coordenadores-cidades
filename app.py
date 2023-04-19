import googlesheets
import streamlit as st

df_coordenadores = googlesheets.get_coordenadores()
df_coordenadores_cidades = googlesheets.get_coordenadores_cidades()

st.title('Dinamica Merchandising')

col1, col2 = st.columns([1.5, 2])

with col1:
    st.subheader("Dados dos Coordenadores")
    st.table(df_coordenadores)

with col2:
    st.subheader("Coordenadores e Cidades")
    st.table(df_coordenadores_cidades)