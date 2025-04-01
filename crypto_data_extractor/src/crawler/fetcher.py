import requests
import json
import boto3
from datetime import datetime, timedelta, timezone
import time
import os
import yfinance as yf
import logging # Adicionar import para logging

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurações
ASSET_TICKER_MAP = {
    'bitcoin': 'BTC-USD',
    'ethereum': 'ETH-USD',
    'cardano': 'ADA-USD',
    'solana':'SOL-USD'
}
ASSETS = list(ASSET_TICKER_MAP.keys()) # ['bitcoin', 'ethereum', 'cardano']
S3_BUCKET = '01.landing'  # Nome do bucket S3
AWS_REGION = 'us-east-2'  # Ajuste para sua região se necessário
HISTORICO_DIR = 'historico/'  # Diretório local (não usado para S3 diretamente)

# Carregue a chave de API do ambiente
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

# Cria o cliente S3
s3_client = boto3.client('s3', region_name=AWS_REGION)

# Cria a pasta 'historico' localmente se não existir (pode ser útil para debug)
if not os.path.exists(HISTORICO_DIR):
    os.makedirs(HISTORICO_DIR)

def check_historical_data_exists(asset_name):
    """Verifica se o arquivo histórico existe no S3 usando o nome do ativo."""
    s3_key = f'historico/{asset_name}_historico.json'
    logging.info(f"Verificando existência do arquivo no S3: {s3_key}")
    try:
        s3_client.head_object(Bucket=S3_BUCKET, Key=s3_key)
        logging.info(f"Arquivo {s3_key} encontrado no S3.")
        return True
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            logging.info(f"Arquivo {s3_key} não encontrado no S3.")
        else:
            logging.error(f"Erro ao verificar arquivo {s3_key} no S3: {e}")
        return False
    except Exception as e:
        logging.error(f"Erro inesperado ao verificar arquivo {s3_key} no S3: {e}")
        return False

def download_historical_data():
    """Baixa dados históricos do Yahoo Finance para todos os ativos e salva no S3."""
    logging.info("Iniciando download de dados históricos...")
    for asset_name, ticker in ASSET_TICKER_MAP.items():
        logging.info(f"Processando ativo: {asset_name} (Ticker: {ticker})")

        # Verifica novamente se o arquivo já existe antes de tentar baixar
        # Isso evita re-download se outro processo criou o arquivo enquanto este esperava
        if check_historical_data_exists(asset_name):
             logging.info(f"Arquivo histórico para {asset_name} já existe no S3. Pulando download.")
             continue

        logging.info(f"Baixando dados históricos para {asset_name} usando ticker {ticker}...")
        try:
            # Baixa todos os dados disponíveis
            data = yf.download(ticker, start="2010-01-01", end=datetime.now().strftime('%Y-%m-%d'))

            # Verifica se os dados foram baixados corretamente
            if data.empty:
                logging.warning(f"Nenhum dado histórico encontrado para {asset_name} (Ticker: {ticker}).")
                continue

            logging.info(f"Dados históricos baixados com sucesso para {asset_name}. Processando {len(data)} registros.")

            # Prepara os dados para JSON
            json_data = []
            for index, row in data.iterrows():
                # Verifica se a linha contém dados válidos (ignora linhas com NaN, por exemplo)
                if row.notna().all():
                    try:
                        # Usa .item() para extrair o valor escalar antes de (opcionalmente) converter
                        # .item() geralmente já retorna o tipo correto (float neste caso)
                        price_value = row['Close'].item()
                        # Garante que é float, embora .item() deva fazer isso
                        price_value = float(price_value)

                        price_info = {
                            'timestamp': index.strftime('%Y-%m-%d %H:%M:%S'),
                            'price_usd': price_value
                        }
                        json_data.append(price_info)
                    except (ValueError, TypeError) as e:
                         logging.warning(f"Erro ao converter/processar preço na linha {index} para {asset_name}: {row['Close']} - {e}")
                         continue # Pula esta linha se a conversão falhar
                else:
                    logging.warning(f"Linha ignorada para {asset_name} em {index} devido a dados ausentes: {row.to_dict()}")

            # Adiciona metadados
            metadata = {
                'extraction_date': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Yahoo Finance',
                'asset_name': asset_name, # Usando o nome original
                'ticker': ticker,
                'total_records': len(json_data)
            }

            # Combina metadados e dados
            output_data = {
                'metadata': metadata,
                'data': json_data
            }

            # Define o nome do arquivo S3 usando o nome original do ativo
            s3_key = f'historico/{asset_name}_historico.json'

            # Faz upload para S3
            logging.info(f"Fazendo upload do arquivo {s3_key} para o bucket {S3_BUCKET}...")
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=json.dumps(output_data, indent=4),  # Agora deve funcionar
                ContentType='application/json'
            )
            logging.info(f"Dados históricos para {asset_name} salvos em {s3_key} no S3.")

        except Exception as e:
            # Captura erros específicos do yfinance ou gerais
            logging.error(f"Falha ao baixar ou processar dados históricos para {asset_name} (Ticker: {ticker}): {e}", exc_info=True)
            # Continua para o próximo ativo em caso de erro
            continue

def fetch_and_upload():
    """Verifica histórico, baixa se necessário, e busca dados diários do CoinGecko."""
    logging.info("Iniciando processo fetch_and_upload.")

    # Verifica se algum arquivo histórico está faltando no S3
    historical_missing = False
    for asset_name in ASSETS:
        if not check_historical_data_exists(asset_name):
            logging.warning(f"Arquivo histórico para {asset_name} não encontrado no S3.")
            historical_missing = True
            break # Se um estiver faltando, precisa baixar todos (ou apenas o que falta)

    # Se algum histórico estiver faltando, chama a função para baixar
    if historical_missing:
        logging.info("Um ou mais arquivos históricos estão faltando. Iniciando download...")
        download_historical_data()
    else:
        logging.info("Todos os arquivos históricos necessários já existem no S3.")

    # --- Continua com a busca de dados diários do CoinGecko ---

    # Calcula a data do dia anterior
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    logging.info(f"Calculada data do dia anterior: {date_str}")

    # Define o intervalo de tempo desejado para CoinGecko
    start_time = datetime.combine(yesterday.date(), datetime.min.time(), tzinfo=timezone.utc)
    end_time = datetime.combine(yesterday.date(), datetime.max.time(), tzinfo=timezone.utc)
    logging.info(f"Intervalo de tempo para CoinGecko: {start_time} a {end_time}")

    for asset_name in ASSETS: # Usa os nomes originais para buscar no CoinGecko
        logging.info(f"Buscando dados diários do CoinGecko para {asset_name} para a data {date_str}...")
        url = f"https://api.coingecko.com/api/v3/coins/{asset_name}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': '2' # Pega 2 dias para garantir a cobertura do dia anterior completo
        }
        try:
            response = requests.get(url, params=params, timeout=30) # Adiciona timeout
            response.raise_for_status() # Levanta erro para status HTTP ruins (4xx ou 5xx)

            data = response.json()
            prices = data.get('prices', [])

            if not prices:
                logging.warning(f"Nenhum dado de preço recebido da API CoinGecko para {asset_name}.")
                continue

            logging.info(f"Recebidos {len(prices)} pontos de preço da CoinGecko para {asset_name}. Filtrando...")

            # Prepara os dados para JSON
            json_data = []
            for price_point in prices:
                if len(price_point) >= 2:
                    try:
                        # Processa os dados se o formato estiver correto
                        timestamp_ms = price_point[0]
                        price_value = price_point[1]
                        timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)

                        # Filtra os dados para incluir apenas os timestamps dentro do intervalo desejado
                        if start_time <= timestamp <= end_time:
                            price_info = {
                                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                                'price_usd': price_value
                            }
                            json_data.append(price_info)
                    except (ValueError, TypeError) as e:
                         logging.warning(f"Erro ao processar ponto de preço {price_point} para {asset_name}: {e}")
                         continue # Pula para o próximo ponto
                else:
                    logging.warning(f"Formato inesperado de price_point para {asset_name}: {price_point}")
                    continue # Ignora este ponto de preço

            logging.info(f"Filtrados {len(json_data)} pontos de preço para {asset_name} no intervalo desejado.")

            if not json_data:
                 logging.warning(f"Nenhum dado de preço encontrado para {asset_name} no intervalo de {start_time} a {end_time}.")
                 continue

            # Adiciona metadados
            metadata = {
                'extraction_date': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'CoinGecko',
                'asset_name': asset_name, # Usando o nome original
                'time_interval': f"{start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
                'total_records': len(json_data)
            }

            # Combina metadados e dados
            output_data = {
                'metadata': metadata,
                'data': json_data
            }

            # Define o nome do arquivo S3
            s3_key = f"cripto/{asset_name}_daily_{date_str}.json"

            # Faz upload para S3
            logging.info(f"Fazendo upload do arquivo {s3_key} para o bucket {S3_BUCKET}...")
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=json.dumps(output_data, indent=4), # Adiciona indentação
                ContentType='application/json'
            )
            logging.info(f"Dados diários para {asset_name} salvos em {s3_key} no S3.")

        except requests.exceptions.RequestException as e:
            logging.error(f"Erro na requisição CoinGecko para {asset_name}: {e}")
        except Exception as e:
            logging.error(f"Erro inesperado ao processar dados CoinGecko para {asset_name}: {e}", exc_info=True)

        # Adiciona um delay entre as requisições da CoinGecko para evitar limites de taxa
        logging.info("Aguardando 2 segundos antes da próxima requisição CoinGecko...")
        time.sleep(2)

    logging.info("Processo fetch_and_upload concluído.")

if __name__ == "__main__":
    fetch_and_upload()
