import duckdb
import constants
from db import DatabaseHandler
from dateutil.relativedelta import relativedelta
from datetime import datetime
class Index():

    def __init__(self, db: DatabaseHandler):
        self.db = db

    def fetchData(self, index_date):
        self.db.updateMarketCap()
        self.db.updateHistoricalMarketCap()
        self.db.updateHistoricalStockPrice()
        end_date = datetime.strptime(index_date, "%Y-%m-%d").date()
        start_date = end_date - relativedelta(months=2)
        print("Data Fetched")
        self.db.executeQuery(f'''
CREATE TEMP VIEW TickerMarketCap AS (
    SELECT 
        cast(addedon as date) as date,
        ticker,
        MAX(marketCap) AS marketCap
    FROM marketCap
    GROUP BY cast(addedon as date), ticker
)''')
        self.db.executeQuery(f'''
CREATE TEMP VIEW TickerPrice AS (
    SELECT 
        cast(addedon as date) as date,
        ticker,
        MAX(price) AS price
    FROM prices
    GROUP BY cast(addedon as date), ticker
)''')

        self.db.executeQuery(f'''
CREATE TEMP VIEW stock_data AS
SELECT 
    mc.ticker,
    pr.date,
    mc.marketCap,
    pr.price
FROM TickerMarketCap mc
INNER JOIN TickerPrice pr 
    ON mc.ticker = pr.ticker 
    AND mc.date = pr.date
WHERE mc.date >= \'{start_date}\' and mc.date <= \'{end_date}\';
''')

        self.db.executeQuery(f'''
CREATE TEMP VIEW ranked_stocks AS
SELECT 
    ticker,
    date,
    ROW_NUMBER() OVER (PARTITION BY date ORDER BY marketCap DESC) AS rank,
    price,
    marketCap
FROM stock_data;
                             ''')
        
        self.db.executeQuery(f'''
CREATE TEMP VIEW selected_stocks AS
SELECT 
    ticker,
    date,
    price,
    marketCap
FROM ranked_stocks
WHERE rank <= 100
order by date asc, marketcap desc;
''')
        

        marketCapData = self.db.executeQuery('select * from selected_stocks')
        
        
        index = self.db.executeQuery(f'''
WITH price_changes AS (
    SELECT 
        ss1.ticker,
        ss1.date,
        (ss1.price / ss2.price - 1) AS price_change
    FROM selected_stocks ss1
    INNER JOIN selected_stocks ss2
        ON ss1.ticker = ss2.ticker
        AND ss1.date = DATE_ADD(ss2.date, INTERVAL 1 DAY) -- Compare to previous day
)
select 
    *,
    EXP(SUM(LN(avg_change)) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)) AS cumulative_index_return
                                     from
                                    (SELECT 
    pc.date,
    (AVG(pc.price_change) + 1) AS avg_change
FROM price_changes pc
GROUP BY pc.date
ORDER BY pc.date) as avg;

''')
        return {'marketCapData': marketCapData, 'indexPerformance' : index}
        
    def createIndex(self, index_date=datetime.now().date().strftime("%Y-%m-%d")):
        return self.fetchData(index_date=index_date)

