# Documentação Unificada dos Scripts de Coleta de Dados de Ações

Aqui contém as documentações detalhadas para os scripts `teste-1.py` e `teste-2.py`, que são projetados para coletar dados de ações financeiras de diferentes fontes: web scraping do Yahoo Finance e API Alpha Vantage, respectivamente.

---

## Documentação do Script `teste-1.py`

### 1. Visão Geral

Este documento detalha o script Python `teste-1.py`, que é projetado para realizar web scraping de dados de ações do Yahoo Finance. O script coleta informações como preço atual, variação, volume, capitalização de mercado e relação P/E para uma lista de símbolos de ações fornecidos. Os dados coletados são então salvos em um arquivo CSV para análise posterior. O script incorpora boas práticas de web scraping, como atrasos aleatórios entre as requisições para evitar bloqueios e tratamento robusto de erros.

### 2. Estrutura do Projeto

O script `teste-1.py` é um arquivo Python autônomo que pode ser executado diretamente. Ele não requer uma estrutura de diretórios complexa, mas cria um diretório `data` (ou o nome especificado pelo usuário) para armazenar os arquivos CSV de saída.

```
. 
├── teste-1.py
└── data/ (diretório de saída para arquivos CSV)
```

### 3. Dependências

O script utiliza as seguintes bibliotecas Python, que devem ser instaladas no ambiente de execução:

- `requests`: Para fazer requisições HTTP para o Yahoo Finance.
- `beautifulsoup4`: Para parsing do HTML e extração dos dados.
- `pandas`: Para manipulação e armazenamento dos dados em DataFrame e exportação para CSV.
- `os`: Para operações de sistema de arquivos, como criação de diretórios.
- `datetime`: Para manipração de datas e horas, usada para timestamp de arquivos.
- `logging`: Para registro de informações, avisos e erros.
- `typing`: Para anotações de tipo, melhorando a legibilidade e manutenibilidade do código.

Para instalar as dependências, utilize o seguinte comando:

```bash
pip install requests beautifulsoup4 pandas
```

### 4. Como Usar

Para executar o script, siga os passos abaixo:

1. Certifique-se de ter o Python 3.x instalado em seu sistema.
2. Instale as dependências listadas na seção anterior.
3. Execute o script a partir da linha de comando:

```bash
python teste-1.py
```

O script coletará os dados das ações predefinidas (`AAPL`, `MSFT`, `GOOGL`, `AMZN`, `META`, `TSLA`, `NVDA`, `JPM`, `JNJ`, `V`) e salvará um arquivo CSV no diretório `data` com um nome baseado na data e hora da execução (ex: `stocks_data_YYYYMMDD_HHMMSS.csv`).

#### 4.1. Personalização

Você pode modificar a lista de símbolos de ações a serem coletados editando a variável `symbols` na função `main()`:

```python
# teste-1.py

def main():
    # ...
    symbols = [\"SUA_ACAO_1\", \"SUA_ACAO_2\", \"SUA_ACAO_3\"]
    # ...
```

Você também pode especificar um diretório de saída diferente ao inicializar a classe `YahooFinanceScraper`:

```python
# teste-1.py

def main():
    # ...
    scraper = YahooFinanceScraper(output_dir=\"meus_dados_acoes\")
    # ...
```

### 5. Detalhes da Implementação

O script é estruturado em torno da classe `YahooFinanceScraper`, que encapsula toda a lógica de web scraping. Abaixo, uma descrição detalhada de suas classes e métodos.

#### 5.1. Classe `YahooFinanceScraper`

Esta classe é responsável por todas as operações de web scraping, desde a requisição HTTP até o parsing do HTML e a extração dos dados.

##### 5.1.1. `__init__(self, output_dir: str = "data")`

- **Descrição**: Construtor da classe. Inicializa as configurações básicas do scraper, como o diretório de saída, a URL base do Yahoo Finance, os cabeçalhos HTTP e uma sessão `requests` para manter as configurações de conexão.
- **Parâmetros**:
    - `output_dir` (str): O diretório onde os arquivos CSV serão salvos. Padrão é `data`.
- **Ações**: Cria o diretório de saída se ele não existir.

##### 5.1.2. `_get_random_delay(self) -> float`

- **Descrição**: Método auxiliar privado que retorna um atraso aleatório entre 1.0 e 3.0 segundos. Isso é crucial para evitar que o scraper seja bloqueado pelo servidor do Yahoo Finance, simulando um comportamento de usuário mais natural.
- **Retorno**: `float` - O tempo de atraso em segundos.

##### 5.1.3. `_fetch_page(self, symbol: str) -> Optional[str]`

- **Descrição**: Método auxiliar privado para buscar o conteúdo HTML da página de uma ação específica no Yahoo Finance.
- **Parâmetros**:
    - `symbol` (str): O símbolo da ação (ex: `AAPL`).
- **Retorno**: `Optional[str]` - O conteúdo HTML da página como uma string, ou `None` em caso de erro (ex: erro de rede, status code diferente de 200).
- **Tratamento de Erros**: Captura exceções `requests.exceptions.RequestException` e registra erros de conexão ou timeout.

##### 5.1.4. `_parse_data(self, html: str, symbol: str) -> Optional[Dict]`

- **Descrição**: Método auxiliar privado que analisa o conteúdo HTML de uma página de ação e extrai os dados relevantes.
- **Parâmetros**:
    - `html` (str): O conteúdo HTML da página.
    - `symbol` (str): O símbolo da ação, usado para identificar elementos específicos na página.
- **Retorno**: `Optional[Dict]` - Um dicionário contendo os dados extraídos da ação (símbolo, nome, preço, variação, volume, capitalização de mercado, P/E, data da coleta e fonte), ou `None` em caso de falha na análise.
- **Extração de Dados**: Utiliza `BeautifulSoup` para encontrar elementos HTML específicos baseados em tags, classes e atributos `data-field` ou `data-test`.
- **Tratamento de Erros**: Captura exceções gerais (`Exception`) durante o parsing e registra erros.

##### 5.1.5. `scrape_stock(self, symbol: str) -> Optional[Dict]`

- **Descrição**: Orquestra o processo de scraping para uma única ação, chamando `_fetch_page` e `_parse_data`.
- **Parâmetros**:
    - `symbol` (str): O símbolo da ação.
- **Retorno**: `Optional[Dict]` - Um dicionário com os dados da ação, ou `None` se a coleta ou análise falhar.

##### 5.1.6. `scrape_multiple_stocks(self, symbols: List[str]) -> pd.DataFrame`

- **Descrição**: Realiza o scraping para uma lista de ações, iterando sobre os símbolos e chamando `scrape_stock` para cada um. Inclui um atraso aleatório entre as requisições para evitar sobrecarga do servidor.
- **Parâmetros**:
    - `symbols` (List[str]): Uma lista de símbolos de ações.
- **Retorno**: `pd.DataFrame` - Um DataFrame do pandas contendo os dados de todas as ações coletadas com sucesso.

##### 5.1.7. `save_to_csv(self, df: pd.DataFrame, filename: str = None) -> str`

- **Descrição**: Salva o DataFrame resultante em um arquivo CSV no diretório de saída especificado.
- **Parâmetros**:
    - `df` (pd.DataFrame): O DataFrame do pandas contendo os dados das ações.
    - `filename` (str, optional): O nome do arquivo CSV. Se `None`, um nome padrão baseado na data e hora atuais será gerado.
- **Retorno**: `str` - O caminho completo do arquivo CSV salvo.

### 5.2. Função `main()`

- **Descrição**: A função principal do script, responsável por inicializar a classe `YahooFinanceScraper`, definir a lista de ações a serem coletadas, iniciar o processo de scraping e salvar os resultados. Também imprime os dados coletados no console.

### 6. Considerações e Limitações

- **Robustez do Web Scraping**: O web scraping é inerentemente frágil. Alterações na estrutura HTML do Yahoo Finance podem quebrar o script. Manutenção regular é necessária.
- **Limitação de Taxa (Rate Limiting)**: Embora o script utilize atrasos aleatórios, requisições excessivas em um curto período podem levar ao bloqueio do IP pelo Yahoo Finance. Para uso em larga escala, proxies ou rotação de IPs podem ser necessários.
- **Dados Disponíveis**: Apenas os dados visíveis na página de cotação do Yahoo Finance são coletados. Informações mais detalhadas (histórico, demonstrações financeiras) exigiriam parsing de outras seções ou o uso de uma API.
- **Legalidade**: O web scraping deve ser feito em conformidade com os termos de serviço do site e as leis de direitos autorais. O uso deste script para fins comerciais ou em larga escala sem permissão pode ser problemático.

### 7. Melhorias Futuras

- **Configuração Externa**: Mover a lista de símbolos de ações e o diretório de saída para um arquivo de configuração (ex: JSON, YAML) para facilitar a personalização sem modificar o código.
- **Tratamento de Erros Aprimorado**: Implementar lógica de repetição (retry mechanism) com backoff exponencial para requisições que falham temporariamente.
- **Paralelização**: Utilizar threads ou processos para coletar dados de múltiplas ações simultaneamente, respeitando os limites de taxa.
- **Interface de Usuário**: Adicionar uma interface de linha de comando (CLI) mais amigável usando bibliotecas como `argparse` ou `Click`.
- **Banco de Dados**: Salvar os dados diretamente em um banco de dados (SQL ou NoSQL) em vez de CSV para facilitar consultas e análises complexas.
- **Dockerização**: Empacotar o script em um contêiner Docker para facilitar a implantação e garantir um ambiente de execução consistente.


---

## Documentação do Script `teste-2.py`

### 1. Visão Geral

Este documento detalha o script Python `teste-2.py`, que é projetado para coletar dados de ações utilizando a API Alpha Vantage. Diferente do `teste-1.py` que usa web scraping, este script interage diretamente com uma API, o que oferece maior robustez e confiabilidade na coleta de dados. Ele é capaz de obter informações como preço atual, variação, volume, capitalização de mercado e relação P/E para uma lista de símbolos de ações fornecidos. Os dados coletados são então salvos em um arquivo CSV para análise posterior. O script gerencia os limites de taxa da API Alpha Vantage e inclui tratamento de erros para requisições e parsing de dados.

### 2. Estrutura do Projeto

O script `teste-2.py` é um arquivo Python autônomo que pode ser executado diretamente. Ele não requer uma estrutura de diretórios complexa, mas cria um diretório `data` (ou o nome especificado pelo usuário) para armazenar os arquivos CSV de saída.

```
. 
├── teste-2.py
└── data/ (diretório de saída para arquivos CSV)
```

### 3. Dependências

O script utiliza as seguintes bibliotecas Python, que devem ser instaladas no ambiente de execução:

- `requests`: Para fazer requisições HTTP para a API Alpha Vantage.
- `pandas`: Para manipulação e armazenamento dos dados em DataFrame e exportação para CSV.
- `os`: Para operações de sistema de arquivos, como criação de diretórios.
- `datetime`: Para manipração de datas e horas, usada para timestamp de arquivos.
- `logging`: Para registro de informações, avisos e erros.
- `typing`: Para anotações de tipo, melhorando a legibilidade e manutenibilidade do código.

Para instalar as dependências, utilize o seguinte comando:

```bash
pip install requests pandas
```

### 4. Como Usar

Para executar o script, siga os passos abaixo:

1. Certifique-se de ter o Python 3.x instalado em seu sistema.
2. Instale as dependências listadas na seção anterior.
3. **Obtenha uma chave de API da Alpha Vantage**: Você precisará de uma chave de API gratuita para usar este script. Obtenha-a em [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key).
4. **Substitua `"YOUR_API_KEY"`**: No script `teste-2.py`, localize a linha `api_key = "YOUR_API_KEY"` dentro da função `main()` e substitua `"YOUR_API_KEY"` pela sua chave de API real.
5. Execute o script a partir da linha de comando:

```bash
python teste-2.py
```

O script coletará os dados das ações predefinidas (`AAPL`, `MSFT`, `GOOGL`, `AMZN`, `META`, `TSLA`, `NVDA`, `JPM`, `JNJ`, `V`) e salvará um arquivo CSV no diretório `data` com um nome baseado na data e hora da execução (ex: `stocks_api_data_YYYYMMDD_HHMMSS.csv`).

#### 4.1. Personalização

Você pode modificar a lista de símbolos de ações a serem coletados editando a variável `symbols` na função `main()`:

```python
# teste-2.py

def main():
    # ...
    symbols = [\"SUA_ACAO_1\", \"SUA_ACAO_2\", \"SUA_ACAO_3\"]
    # ...
```

Você também pode especificar um diretório de saída diferente ao inicializar a classe `AlphaVantageCollector`:

```python
# teste-2.py

def main():
    # ...
    collector = AlphaVantageCollector(api_key, output_dir=\"meus_dados_api\")
    # ...
```

### 5. Detalhes da Implementação

O script é estruturado em torno da classe `AlphaVantageCollector`, que encapsula toda a lógica de interação com a API Alpha Vantage. Abaixo, uma descrição detalhada de suas classes e métodos.

#### 5.1. Classe `AlphaVantageCollector`

Esta classe é responsável por todas as operações de coleta de dados via API, desde a requisição HTTP até o parsing das respostas JSON e a extração dos dados.

##### 5.1.1. `__init__(self, api_key: str, output_dir: str = "data")`

- **Descrição**: Construtor da classe. Inicializa as configurações básicas do coletor, como a chave da API, o diretório de saída, a URL base da API Alpha Vantage e uma sessão `requests`. Também verifica se a chave da API foi fornecida.
- **Parâmetros**:
    - `api_key` (str): Sua chave de API da Alpha Vantage.
    - `output_dir` (str): O diretório onde os arquivos CSV serão salvos. Padrão é `data`.
- **Ações**: Cria o diretório de saída se ele não existir. Emite um aviso se a chave da API não for fornecida ou for a string padrão `"YOUR_API_KEY"`.

##### 5.1.2. `_make_request(self, function: str, symbol: str, **kwargs) -> Optional[Dict]`

- **Descrição**: Método auxiliar privado para fazer requisições à API Alpha Vantage. Constrói a URL da requisição com base na função da API, símbolo da ação e parâmetros adicionais.
- **Parâmetros**:
    - `function` (str): A função da API a ser chamada (ex: `GLOBAL_QUOTE`, `OVERVIEW`).
    - `symbol` (str): O símbolo da ação (ex: `AAPL`).
    - `**kwargs`: Argumentos de palavra-chave adicionais para a requisição da API.
- **Retorno**: `Optional[Dict]` - A resposta JSON da API como um dicionário, ou `None` em caso de erro (ex: erro de rede, status code diferente de 200, mensagem de erro da API).
- **Tratamento de Erros**: Captura exceções `requests.exceptions.RequestException` e verifica mensagens de erro ou informação retornadas pela própria API Alpha Vantage.

##### 5.1.3. `_parse_quote_data(self, data: Dict, symbol: str) -> Optional[Dict]`

- **Descrição**: Método auxiliar privado que analisa os dados de cotação (`GLOBAL_QUOTE`) retornados pela API e os formata em um dicionário padronizado.
- **Parâmetros**:
    - `data` (Dict): Os dados brutos da API para a função `GLOBAL_QUOTE`.
    - `symbol` (str): O símbolo da ação.
- **Retorno**: `Optional[Dict]` - Um dicionário contendo os dados de cotação formatados (símbolo, nome - que é o próprio símbolo nesta função, preço, variação, volume, data da coleta e fonte), ou `None` em caso de falha na análise ou estrutura de dados inesperada.
- **Limitação**: A função `GLOBAL_QUOTE` não fornece o nome completo da empresa, capitalização de mercado ou relação P/E, que são marcados como `"N/A"`.

##### 5.1.4. `_parse_overview_data(self, data: Dict, symbol: str) -> Optional[Dict]`

- **Descrição**: Método auxiliar privado que analisa os dados de visão geral da empresa (`OVERVIEW`) retornados pela API e os formata em um dicionário padronizado.
- **Parâmetros**:
    - `data` (Dict): Os dados brutos da API para a função `OVERVIEW`.
    - `symbol` (str): O símbolo da ação.
- **Retorno**: `Optional[Dict]` - Um dicionário contendo os dados de visão geral formatados (símbolo, nome, capitalização de mercado, P/E, data da coleta e fonte), ou `None` em caso de falha na análise ou estrutura de dados inesperada.
- **Limitação**: A função `OVERVIEW` não fornece preço, variação ou volume, que são marcados como `"N/A"`.

##### 5.1.5. `get_stock_quote(self, symbol: str) -> Optional[Dict]`

- **Descrição**: Obtém a cotação atual de uma ação usando a função `GLOBAL_QUOTE` da API.
- **Parâmetros**:
    - `symbol` (str): O símbolo da ação.
- **Retorno**: `Optional[Dict]` - Um dicionário com os dados de cotação da ação, ou `None` se a coleta falhar.

##### 5.1.6. `get_company_overview(self, symbol: str) -> Optional[Dict]`

- **Descrição**: Obtém informações gerais sobre uma empresa usando a função `OVERVIEW` da API.
- **Parâmetros**:
    - `symbol` (str): O símbolo da ação.
- **Retorno**: `Optional[Dict]` - Um dicionário com
(Content truncated due to size limit. Use page ranges or line ranges to read remaining content)


## Autor

Lauro Bonometti
