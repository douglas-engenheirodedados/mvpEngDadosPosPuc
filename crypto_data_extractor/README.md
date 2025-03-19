# Crypto Data Extractor

Este projeto é um extrator de dados de preços de criptomoedas que utiliza a API do CoinGecko para coletar informações sobre os preços diários de ativos como Bitcoin, Ethereum e Cardano. Os dados são salvos localmente em formato JSON.

## Pré-requisitos

Antes de executar o script, você precisa ter o seguinte instalado:

- Python 3.x
- Bibliotecas Python: `requests`, `boto3` (opcional, se você planeja usar o S3)

Você pode instalar as bibliotecas necessárias usando o seguinte comando:
```bash
pip install requests boto3
```

## Configuração

1. **Chave da API**: Embora a API do CoinGecko não exija uma chave de API para a maioria das requisições, você pode definir uma variável de ambiente `COINGECKO_API_KEY` caso precise de autenticação para outros serviços.

2. **Estrutura de Diretórios**: O script cria uma pasta chamada `data` para armazenar os arquivos JSON gerados. Certifique-se de que você tenha permissão para criar diretórios no local onde o script está sendo executado.

## Como Funciona

O script realiza as seguintes etapas:

1. **Cálculo da Data do Dia Anterior**: O script calcula a data do dia anterior para buscar os dados de preços.

2. **Requisição à API do CoinGecko**: O script faz uma requisição à API do CoinGecko para obter os dados de preços diários dos ativos especificados. A requisição é feita para os últimos 2 dias, mas os dados são filtrados para incluir apenas os do dia anterior.

3. **Filtragem dos Dados**: Os dados recebidos são filtrados para incluir apenas os timestamps que estão dentro do intervalo de 00:00 a 23:59 do dia anterior.

4. **Salvamento dos Dados**: Os dados filtrados são salvos em arquivos JSON na pasta `data`. O nome do arquivo segue o formato `{asset}_daily_{date}.json`, onde `{asset}` é o nome do ativo (por exemplo, bitcoin) e `{date}` é a data do dia anterior.

## Execução

Para executar o script, use o seguinte comando:
```bash
python src/crawler/fetcher.py
```

## Agendamento

Para automatizar a execução do script, você pode configurar um cron job (em sistemas Unix/Linux) ou usar o Agendador de Tarefas do Windows. Por exemplo, para executar o script todos os dias às 00:05 AM, adicione a seguinte linha ao seu crontab:


## Contribuição

Sinta-se à vontade para contribuir com melhorias ou correções. Para isso, faça um fork do repositório e envie um pull request.