import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


def get_sheet():
    # Carrega as credenciais do arquivo JSON
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

    # Autentica com o Google Drive
    client = gspread.authorize(creds)

    # Abre a planilha pelo ID
    sheet_id = '1KORPIA-Rp6CsZE6dwKnps7JM61KyVUNGvWwms-5TqjM'
    sheet = client.open_by_key(sheet_id)

    return sheet

def get_coordenadores():

    sheet = get_sheet()

    # Seleciona a primeira guia da planilha
    data = sheet.get_worksheet(0)
    # Lê a tabela e salva como um objeto Pandas DataFrame
    data = data.get_all_values()

    df_coodenador = pd.DataFrame(data=data, columns=['Gerente', 'Coordenador', 'e-mail', 'Telefone'])
    df_coodenador = df_coodenador.drop(index = 0, axis = 0)

    return df_coodenador

def get_coordenadores_cidades():

    sheet = get_sheet()

    # Seleciona a primeira guia da planilha
    data = sheet.get_worksheet(1)
    # Lê a tabela e salva como um objeto Pandas DataFrame
    data = data.get_all_values()

    df_coodenador_cidade = pd.DataFrame(data=data, columns=['Gerente', 'Coordenador', 'e-mail', 'Telefone'])
    df_coodenador_cidade = df_coodenador_cidade.drop(index = 0, axis = 0)

    return df_coodenador_cidade
