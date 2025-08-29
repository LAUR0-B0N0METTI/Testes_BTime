"""
Script para coleta de dados de ações via web scraping do Yahoo Finance.
Este script extrai informações de ações como preço atual, variação, volume, etc.
e salva os dados em um arquivo CSV.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
from datetime import datetime
import logging
from typing import Dict, List, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YahooFinanceScraper:
    """
    Classe para realizar web scraping de dados de ações do Yahoo Finance.
    """
    
    def __init__(self, output_dir: str = "data"):
        """
        Inicializa o scraper com o diretório de saída.
        
        Args:
            output_dir (str): Diretório onde os arquivos CSV serão salvos.
        """
        self.output_dir = output_dir
        self.base_url = "https://finance.yahoo.com/quote/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Criar diretório de saída se não existir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _get_random_delay(self) -> float:
        """
        Retorna um atraso aleatório para evitar bloqueios.
        
        Returns:
            float: Atraso em segundos.
        """
        return random.uniform(1.0, 3.0)
    
    def _fetch_page(self, symbol: str) -> Optional[str]:
        """
        Busca a página da ação no Yahoo Finance.
        
        Args:
            symbol (str): Símbolo da ação (ex: AAPL, MSFT).
            
        Returns:
            Optional[str]: Conteúdo HTML da página ou None em caso de falha.
        """
        url = f"{self.base_url}{symbol}"
        
        try:
            logger.info(f"Buscando dados para {symbol}...")
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Status code {response.status_code} para {symbol}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar dados para {symbol}: {str(e)}")
            return None
    
    def _parse_data(self, html: str, symbol: str) -> Optional[Dict]:
        """
        Extrai os dados da ação do HTML.
        
        Args:
            html (str): Conteúdo HTML da página.
            symbol (str): Símbolo da ação.
            
        Returns:
            Optional[Dict]: Dicionário com os dados da ação ou None em caso de falha.
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extrair o nome da ação
            name_element = soup.find('h1', {'class': 'D(ib) Fz(18px)'})
            name = name_element.text.split('(')[0].strip() if name_element else symbol
            
            # Extrair o preço atual
            price_element = soup.find('fin-streamer', {'data-field': 'regularMarketPrice', 'data-symbol': symbol})
            price = price_element.text if price_element else "N/A"
            
            # Extrair a variação
            change_element = soup.find('fin-streamer', {'data-field': 'regularMarketChange', 'data-symbol': symbol})
            change = change_element.text if change_element else "N/A"
            
            # Extrair a variação percentual
            change_percent_element = soup.find('fin-streamer', {'data-field': 'regularMarketChangePercent', 'data-symbol': symbol})
            change_percent = change_percent_element.text if change_percent_element else "N/A"
            
            # Extrair o volume
            volume_element = soup.find('fin-streamer', {'data-field': 'regularMarketVolume', 'data-symbol': symbol})
            volume = volume_element.text if volume_element else "N/A"
            
            # Extrair a capitalização de mercado
            market_cap_element = soup.find('td', {'data-test': 'MARKET_CAP-value'})
            market_cap = market_cap_element.text if market_cap_element else "N/A"
            
            # Extrair a relação P/E
            pe_ratio_element = soup.find('td', {'data-test': 'PE_RATIO-value'})
            pe_ratio = pe_ratio_element.text if pe_ratio_element else "N/A"
            
            # Data da coleta
            collection_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                'symbol': symbol,
                'name': name,
                'price': price,
                'change': change,
                'change_percent': change_percent,
                'volume': volume,
                'market_cap': market_cap,
                'pe_ratio': pe_ratio,
                'collection_date': collection_date,
                'source': 'Yahoo Finance (Web Scraping)'
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar dados para {symbol}: {str(e)}")
            return None
    
    def scrape_stock(self, symbol: str) -> Optional[Dict]:
        """
        Realiza o scraping completo para uma ação.
        
        Args:
            symbol (str): Símbolo da ação.
            
        Returns:
            Optional[Dict]: Dicionário com os dados da ação ou None em caso de falha.
        """
        html = self._fetch_page(symbol)
        if not html:
            return None
            
        data = self._parse_data(html, symbol)
        if not data:
            return None
            
        return data
    
    def scrape_multiple_stocks(self, symbols: List[str]) -> pd.DataFrame:
        """
        Realiza o scraping para múltiplas ações.
        
        Args:
            symbols (List[str]): Lista de símbolos de ações.
            
        Returns:
            pd.DataFrame: DataFrame com os dados de todas as ações.
        """
        all_data = []
        
        for symbol in symbols:
            data = self.scrape_stock(symbol)
            if data:
                all_data.append(data)
            
            # Adicionar um atraso aleatório para evitar bloqueios
            time.sleep(self._get_random_delay())
        
        return pd.DataFrame(all_data)
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = None) -> str:
        """
        Salva o DataFrame em um arquivo CSV.
        
        Args:
            df (pd.DataFrame): DataFrame com os dados das ações.
            filename (str, optional): Nome do arquivo. Se None, usa um nome baseado na data.
            
        Returns:
            str: Caminho do arquivo salvo.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stocks_data_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Dados salvos em {filepath}")
        
        return filepath


def main():
    """
    Função principal para executar o scraping de ações.
    """
    # Lista de símbolos de ações para coletar
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'JNJ', 'V']
    
    # Inicializar o scraper
    scraper = YahooFinanceScraper()
    
    # Coletar dados das ações
    stocks_data = scraper.scrape_multiple_stocks(symbols)
    
    if not stocks_data.empty:
        # Salvar os dados em um arquivo CSV
        scraper.save_to_csv(stocks_data)
        print("\nDados coletados com sucesso!")
        print(stocks_data)
    else:
        print("Não foi possível coletar dados das ações.")


if __name__ == "__main__":
    main()