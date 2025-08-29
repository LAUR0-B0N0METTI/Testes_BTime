"""
Script para coleta de dados de ações via API Alpha Vantage.
Este script acessa a API Alpha Vantage para obter informações de ações
e salva os dados em um arquivo CSV.
"""

import requests
import pandas as pd
import os
import time
from datetime import datetime
import logging
from typing import Dict, List, Optional, Union

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AlphaVantageCollector:
    """
    Classe para coletar dados de ações usando a API Alpha Vantage.
    """
    
    def __init__(self, api_key: str, output_dir: str = "data"):
        """
        Inicializa o coletor com a chave da API e diretório de saída.
        
        Args:
            api_key (str): Chave da API Alpha Vantage.
            output_dir (str): Diretório onde os arquivos CSV serão salvos.
        """
        self.api_key = api_key
        self.output_dir = output_dir
        self.base_url = "https://www.alphavantage.co/query"
        self.session = requests.Session()
        
        # Criar diretório de saída se não existir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Verificar se a chave da API foi fornecida
        if not api_key or api_key == "YOUR_API_KEY":
            logger.warning("Chave da API não fornecida. Por favor, obtenha uma chave gratuita em https://www.alphavantage.co/support/#api-key")
    
    def _make_request(self, function: str, symbol: str, **kwargs) -> Optional[Dict]:
        """
        Faz uma requisição à API Alpha Vantage.
        
        Args:
            function (str): Função da API a ser chamada.
            symbol (str): Símbolo da ação.
            **kwargs: Parâmetros adicionais da API.
            
        Returns:
            Optional[Dict]: Resposta da API ou None em caso de falha.
        """
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': self.api_key,
            **kwargs
        }
        
        try:
            logger.info(f"Fazendo requisição para {symbol}...")
            response = self.session.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar se há mensagem de erro na resposta
                if "Error Message" in data:
                    logger.error(f"Erro na API: {data['Error Message']}")
                    return None
                elif "Information" in data:
                    logger.warning(f"Informação da API: {data['Information']}")
                    return None
                    
                return data
            else:
                logger.warning(f"Status code {response.status_code} para {symbol}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao fazer requisição para {symbol}: {str(e)}")
            return None
    
    def _parse_quote_data(self, data: Dict, symbol: str) -> Optional[Dict]:
        """
        Analisa os dados de cotação da API.
        
        Args:
            data (Dict): Dados brutos da API.
            symbol (str): Símbolo da ação.
            
        Returns:
            Optional[Dict]: Dicionário com os dados formatados ou None em caso de falha.
        """
        try:
            if "Global Quote" not in data:
                logger.error("Estrutura de dados inesperada na resposta da API")
                return None
                
            quote = data["Global Quote"]
            
            # Mapear os campos da API para nomes mais amigáveis
            return {
                'symbol': symbol,
                'name': symbol,  # A API não retorna o nome da empresa na função GLOBAL_QUOTE
                'price': quote.get('05. price', "N/A"),
                'change': quote.get('09. change', "N/A"),
                'change_percent': quote.get('10. change percent', "N/A"),
                'volume': quote.get('06. volume', "N/A"),
                'market_cap': "N/A",  # Não disponível nesta função da API
                'pe_ratio': "N/A",    # Não disponível nesta função da API
                'collection_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'source': 'Alpha Vantage API'
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar dados para {symbol}: {str(e)}")
            return None
    
    def _parse_overview_data(self, data: Dict, symbol: str) -> Optional[Dict]:
        """
        Analisa os dados de visão geral da empresa da API.
        
        Args:
            data (Dict): Dados brutos da API.
            symbol (str): Símbolo da ação.
            
        Returns:
            Optional[Dict]: Dicionário com os dados formatados ou None em caso de falha.
        """
        try:
            if "Symbol" not in data:
                logger.error("Estrutura de dados inesperada na resposta da API")
                return None
                
            # Mapear os campos da API para nomes mais amigáveis
            return {
                'symbol': symbol,
                'name': data.get('Name', symbol),
                'price': "N/A",  # Não disponível nesta função da API
                'change': "N/A",  # Não disponível nesta função da API
                'change_percent': "N/A",  # Não disponível nesta função da API
                'volume': "N/A",  # Não disponível nesta função da API
                'market_cap': data.get('MarketCapitalization', "N/A"),
                'pe_ratio': data.get('PERatio', "N/A"),
                'collection_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'source': 'Alpha Vantage API'
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar dados para {symbol}: {str(e)}")
            return None
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """
        Obtém a cotação atual de uma ação.
        
        Args:
            symbol (str): Símbolo da ação.
            
        Returns:
            Optional[Dict]: Dicionário com os dados da ação ou None em caso de falha.
        """
        data = self._make_request("GLOBAL_QUOTE", symbol)
        if not data:
            return None
            
        return self._parse_quote_data(data, symbol)
    
    def get_company_overview(self, symbol: str) -> Optional[Dict]:
        """
        Obtém informações gerais sobre uma empresa.
        
        Args:
            symbol (str): Símbolo da ação.
            
        Returns:
            Optional[Dict]: Dicionário com os dados da empresa ou None em caso de falha.
        """
        data = self._make_request("OVERVIEW", symbol)
        if not data:
            return None
            
        return self._parse_overview_data(data, symbol)
    
    def get_complete_stock_data(self, symbol: str) -> Optional[Dict]:
        """
        Obtém dados completos de uma ação, combinando cotação e informações da empresa.
        
        Args:
            symbol (str): Símbolo da ação.
            
        Returns:
            Optional[Dict]: Dicionário com os dados completos da ação ou None em caso de falha.
        """
        # Obter dados de cotação
        quote_data = self.get_stock_quote(symbol)
        if not quote_data:
            return None
            
        # Obter dados da empresa
        overview_data = self.get_company_overview(symbol)
        
        # Combinar os dados
        if overview_data:
            # Substituir os campos N/A da cotação com os dados da empresa quando disponíveis
            for key, value in overview_data.items():
                if quote_data.get(key) == "N/A" and value != "N/A":
                    quote_data[key] = value
        
        return quote_data
    
    def get_multiple_stocks_data(self, symbols: List[str]) -> pd.DataFrame:
        """
        Obtém dados para múltiplas ações.
        
        Args:
            symbols (List[str]): Lista de símbolos de ações.
            
        Returns:
            pd.DataFrame: DataFrame com os dados de todas as ações.
        """
        all_data = []
        
        for symbol in symbols:
            data = self.get_complete_stock_data(symbol)
            if data:
                all_data.append(data)
            
            # Respeitar os limites de taxa da API (5 chamadas por minuto para a conta gratuita)
            time.sleep(12)  # 60 segundos / 5 chamadas = 12 segundos por chamada
        
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
            filename = f"stocks_api_data_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Dados salvos em {filepath}")
        
        return filepath


def main():
    """
    Função principal para executar a coleta de dados via API.
    """
    # Substitua "YOUR_API_KEY" pela sua chave da API Alpha Vantage
    # Você pode obter uma chave gratuita em https://www.alphavantage.co/support/#api-key
    api_key = "YOUR_API_KEY"
    
    # Lista de símbolos de ações para coletar
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'JNJ', 'V']
    
    # Inicializar o coletor
    collector = AlphaVantageCollector(api_key)
    
    # Coletar dados das ações
    stocks_data = collector.get_multiple_stocks_data(symbols)
    
    if not stocks_data.empty:
        # Salvar os dados em um arquivo CSV
        collector.save_to_csv(stocks_data)
        print("\nDados coletados com sucesso!")
        print(stocks_data)
    else:
        print("Não foi possível coletar dados das ações.")


if __name__ == "__main__":
    main()