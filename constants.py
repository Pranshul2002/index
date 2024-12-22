ALL_STOCK_MARKET_CAP="https://api.nasdaq.com/api/screener/stocks?tableonly=false&download=true"
FMP_BASE_URL="https://financialmodelingprep.com/api/v3/historical-market-capitalization/"
FMP_API_KEY ='fN6pVsztWpHPC2JJYquEl8791YDjuagI'
FINHUBB_API_KEY='ctit7l9r01qgfbsvg0sgctit7l9r01qgfbsvg0t0'
PRICE_BASE_URL='https://finnhub.io/docs/api'
CREATE_STOCKS = '''
CREATE TABLE IF NOT EXISTS STOCKS(
    ticker VARCHAR PRIMARY KEY, 
    name VARCHAR,
    industry VARCHAR,
    sector VARCHAR,
    country VARCHAR
);'''
CREATE_MARKETCAP='''
CREATE SEQUENCE IF NOT EXISTS marketCap_sequence START 1;
CREATE TABLE IF NOT EXISTS MARKETCAP(
    marketCap double,
    marketCapID int primary key DEFAULT nextval('marketCap_sequence'),
    ticker VARCHAR,
    addedOn DATETIME,
    FOREIGN KEY (ticker) REFERENCES STOCKS(ticker)
);
'''
CREATE_PRICES='''
CREATE SEQUENCE IF NOT EXISTS prices_sequence START 1;
CREATE TABLE IF NOT EXISTS PRICES(
    priceID INT PRIMARY KEY DEFAULT nextval('prices_sequence'),
    ticker VARCHAR,
    addedOn DATETIME,
    price double,
    FOREIGN KEY (ticker) REFERENCES STOCKS(ticker)
);'''