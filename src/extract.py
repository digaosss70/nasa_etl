import sys
sys.path.insert(0, '/home/rodrigo/ED_PROJECTS/nasa_etl')

import requests
import pandas as pd
import os
from dotenv import load_dotenv
from config.api import DIAS_PARA_EXTRAIR,ROVER_PARA_EXTRAIR
import datetime

load_dotenv()

# Substitua 'SUA_CHAVE_DE_API_AQUI' pela sua chave de API da NASA
api_key = os.getenv("NASA_API_KEY")


def obter_dados_api(url):
    # Fazendo a solicitação GET para a API
    response = requests.get(url)

    # Verificando se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Convertendo a resposta para formato JSON
        data = response.json()
        # Retornando os dados
        return data
    else:
        print("Erro ao acessar a API")

df = pd.DataFrame()

for i in range(DIAS_PARA_EXTRAIR):
    # Calculando a data de hoje menos o número de dias para extrair
    data = datetime.datetime.now() - datetime.timedelta(days=i)
    # Formatando a data no formato YYYY-MM-DD
    data_formatada = data.strftime("%Y-%m-%d")
    # URL da API para coletar informações dos ROVERS
    url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{ROVER_PARA_EXTRAIR}/photos?earth_date={data_formatada}&api_key={api_key}"


    # Obtendo os dados da API
    dados = obter_dados_api(url)

    # Inicializando uma lista para armazenar os dados do rover
    photo_data = []
    for photo in dados['photos']:
        photo_data.append({
            'photo_id': photo['id'],
            'sol': photo['sol'],
            'camera_id': photo['camera']['id'],
            'camera_name': photo['camera']['name'],
            'camera_full_name': photo['camera']['full_name'],
            'img_src': photo['img_src'],
            'earth_date': photo['earth_date'],
            'rover_id': photo['rover']['id'],
            'rover_name': photo['rover']['name'],
            'rover_landing_date': photo['rover']['landing_date'],
            'rover_launch_date': photo['rover']['launch_date'],
            'rover_status': photo['rover']['status'],
        })

    # Criando o DataFrame a partir da lista de dicionários
    df = pd.DataFrame(photo_data)

    # Salvar o DataFrame em formato CSV
    df.to_csv(f"data/csv/{ROVER_PARA_EXTRAIR}_{data_formatada}.csv", index=False)

    # Criar o diretório para salvar as fotos
    directory = f"data/photos/{ROVER_PARA_EXTRAIR}/{data_formatada}"
    os.makedirs(directory, exist_ok=True)

    # Baixar cada uma das fotos e salvar no diretório
    for photo in photo_data:
        img_url = photo['img_src']
        img_name = os.path.join(directory, f"{photo['photo_id']}.jpg")
        response = requests.get(img_url)
        if response.status_code == 200:
            with open(img_name, 'wb') as img_file:
                img_file.write(response.content)
                print(f"baixei a imagem: {img_name}")