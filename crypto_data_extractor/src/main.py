from crawler.crypto_crawler import CryptoCrawler

def main():
    try:
        crawler = CryptoCrawler()
        crawler.start_monitoring()
    except KeyboardInterrupt:
        print("\nMonitoramento interrompido pelo usuário")
    except Exception as e:
        print(f"Erro fatal: {e}")

if __name__ == "__main__":
    main()
