from src.crawler.fetcher import fetch_and_upload

def lambda_handler(event, context):
    fetch_and_upload()