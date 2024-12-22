import duckdb
import constants
import time
from helper import Helper
from dateutil.relativedelta import relativedelta
from datetime import datetime

class DatabaseHandler():
    notListedStocks = ['BRK/A', 'BRK/B', 'GEV']
    def __init__(self, databaseFile, mode='PRESIST'):
        connection_string = ':' + mode + ':' +databaseFile if mode == 'memory' else databaseFile
        self.databaseConnection = duckdb.connect(database=connection_string)
        self.db = self.databaseConnection.sql
        self.initializeDatabase()
    
    def executeQuery(self, query):
        data = self.db(query)
        return data.df() if data is not None else data

    def initializeDatabase(self):
        self.db('BEGIN;')
        self.db(constants.CREATE_STOCKS)
        self.db(constants.CREATE_MARKETCAP)
        self.db(constants.CREATE_PRICES)
        self.db('COMMIT;')
        print("Database Initialized successfully")

    def updateMarketCap(self):
        stock_count = self.executeQuery('select count(1) from stocks')['count(1)'][0]
        helper = Helper()
        
        rows = helper.fetch_market_cap_data()
        current_timestamp = datetime.now()
        self.db('BEGIN;')
        for data in rows:
            if stock_count == 0:
                self.db('insert into stocks (ticker, name, industry, sector, country) values (?,?,?,?,?);', params=(data['symbol'],data['name'],data['industry'],data['sector'],data['country']))
            self.db('insert into marketcap (ticker, marketCap, addedOn) values (?,?,?);', params=(data['symbol'], float(data['marketCap']) if len(data['marketCap']) > 0 else 0 , current_timestamp))
        self.db('COMMIT;')

    def updateHistoricalMarketCap(self, start_date=datetime.now().date(), go_back_months=12):
        print("Fetching historical market cap data")
        helper = Helper()
        top_150_stocks = self.executeQuery('select stocks.*, mp.marketcap from (select row_number() over (partition by ticker order by addedon desc) as rnk, ticker, marketcap from marketcap) as mp inner join stocks on stocks.ticker=mp.ticker where rnk=1 order by mp.marketCap desc limit 150;')
        for stock in top_150_stocks['ticker']:
            previousDate = start_date - relativedelta(months=go_back_months)
            previousDate = previousDate.strftime("%Y-%m-%d")
            tickerCount = self.db('select count(1) as cnt from marketCap where ticker=? and addedOn=?', params=(stock,previousDate)).df()['cnt'][0]
            if tickerCount == 0 and stock not in self.notListedStocks:
                historical_data = helper.fetch_historical_market_cap_data(stock, go_back_months=go_back_months, start_date=start_date, retries=5)
                time.sleep(0.5)
                self.db('BEGIN;')
                for data in historical_data:
                    self.db('insert into marketcap (ticker, marketCap, addedOn) values (?,?,?);', params=(data['symbol'], data['marketCap'], datetime.strptime(data['date'], "%Y-%m-%d")))
                self.db('COMMIT;')

    def updateHistoricalStockPrice(self, start_date=datetime.now().date(), go_back_months=3):
        print("Fetching historical stock data")
        helper = Helper()
        top_150_stocks = self.executeQuery('select stocks.*, mp.marketcap from (select row_number() over (partition by ticker order by addedon desc) as rnk, ticker, marketcap from marketcap) as mp inner join stocks on stocks.ticker=mp.ticker where rnk=1 order by mp.marketCap desc limit 150;')
        for stock in top_150_stocks['ticker']:
            previousDate = start_date - relativedelta(months=go_back_months) + relativedelta(days=1)
            previousDate = previousDate.strftime("%Y-%m-%d")
            tickerCount = self.db('select count(1) as cnt from prices where ticker=? and addedOn=?', params=(stock,previousDate)).df()['cnt'][0]
            if tickerCount == 0 and stock not in self.notListedStocks:
                print(stock)
                historical_data = helper.fetch_historical_stock_data(stock, go_back_months=go_back_months)
                self.db('BEGIN;')
                for date, price in zip(historical_data.index, historical_data['Close']):
                    parsed_date = date.date().strftime('%Y-%m-%d')
                    self.db('insert into prices (ticker, price, addedOn) values (?,?,?);', params=(stock, price, parsed_date))
                self.db('COMMIT;')