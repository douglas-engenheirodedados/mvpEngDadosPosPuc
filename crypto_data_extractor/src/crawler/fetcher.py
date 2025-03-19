import requests
import json
import boto3
from datetime import datetime, timedelta, timezone
import time
import os

# Configurações
ASSETS = ['bitcoin', 'ethereum', 'cardano']  # Adicione outros ativos
# S3_BUCKET = '01.landing'  # Comentado para salvar localmente
# S3_FOLDER = 'crypto/prices/'  # Pasta dentro do bucket (opcional) - Comentado
AWS_REGION = 'us-east-2'  # Ajuste para sua região se necessário

# Carregue a chave de API do ambiente
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

# Cria a pasta 'data' se não existir
if not os.path.exists('data'):
    os.makedirs('data')

def fetch_and_upload():
    # s3_client = boto3.client('s3', region_name=AWS_REGION)  # Comentado para não usar S3

    # Calcula a data do dia anterior
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')  # Formato da data para o nome do arquivo

    # Define o intervalo de tempo desejado
    start_time = datetime.combine(yesterday.date(), datetime.min.time(), tzinfo=timezone.utc)  # 00:00
    end_time = datetime.combine(yesterday.date(), datetime.max.time(), tzinfo=timezone.utc)  # 23:59

    for asset in ASSETS:
        print(f"Fetching {asset} daily prices for {date_str}...")
        url = f"https://api.coingecko.com/api/v3/coins/{asset}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': '2'  # Obtenha dados diários
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            prices = data.get('prices', [])

            if not prices:
                print("Nenhum dado recebido da API.")
                continue

            # Prepara os dados para JSON
            json_data = []
            for price_point in prices:
                if len(price_point) < 2:  # Verifica se há pelo menos 2 elementos
                    print(f"Aviso: formato inesperado de price_point: {price_point}")
                    continue  # Ignora este ponto de preço

                # Processa os dados se o formato estiver correto
                timestamp = datetime.fromtimestamp(price_point[0] / 1000, tz=timezone.utc)
                
                # Filtra os dados para incluir apenas os timestamps dentro do intervalo desejado
                if start_time <= timestamp <= end_time:
                    price_info = {
                        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'price_usd': price_point[1]
                    }
                    json_data.append(price_info)

            # Define o nome do arquivo
            file_name = f"data/{asset}_daily_{date_str}.json"  # Salva na pasta 'data'

            # Salva o arquivo localmente
            with open(file_name, 'w') as json_file:
                json.dump(json_data, json_file, indent=4)  # Converte os dados para JSON e salva com indentação

            # Comentado: Faz upload para S3
            # s3_client.put_object(
            #     Bucket=S3_BUCKET,
            #     Key=file_name,
            #     Body=json.dumps(json_data),  # Converte os dados para JSON
            #     ContentType='application/json'  # Define o tipo de conteúdo como JSON
            # )
            print(f"Saved {file_name} locally.")
        else:
            print(f"Error fetching {asset}: Status {response.status_code}")
        
        time.sleep(2)  # Adicione um delay de 2 segundos entre as requisições

if __name__ == "__main__":
    fetch_and_upload()
