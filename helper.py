import requests
import constants
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import yfinance as yf

class Helper:

    def make_api_call(self, api_url, method="GET", headers=None, params=None, data=None, timeout=5):
        try:
            response = requests.request(
                method=method,
                url=api_url,
                headers=headers,
                params=params,
                data=data,
                timeout=timeout
            )
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.Timeout:
            raise Exception(f"API call to {api_url} timed out after {timeout} seconds.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API call to {api_url} failed: {e}")
        
    def compare_market_cap_data(self, a, b):
        if a[1] < b[1]:
            return -1
        elif a[1] > b[1]:
            return 1
        else:
            return 0
        

    def fetch_historical_market_cap_data(self ,ticker ,go_back_months, start_date ,retries=3):
        headers = {
            "User-Agent": "INDEX",
            "Accept": "application/json",
        }
        historical_data = []
        attempt = 0
        while attempt < retries:
            try:
                previousDate = start_date - relativedelta(months=go_back_months)
                api_url = constants.FMP_BASE_URL + ticker + '?from=' + previousDate.strftime("%Y-%m-%d") + '&to=' + start_date.strftime("%Y-%m-%d") + '&apikey=' + constants.FMP_API_KEY
                historical_data = self.make_api_call(api_url=api_url, headers=headers, timeout=10)
                return historical_data
            except Exception as e:
                # Log the exception or print an error (optional)
                print(f"Attempt {attempt + 1} failed: {e}")
                
                # If it's the last attempt, raise the error
                if attempt == retries - 1:
                    raise
                else:
                    # Wait for a short period before retrying (e.g., 2 seconds)
                    time.sleep(2)
            
            attempt += 1
        return historical_data

    
    def fetch_market_cap_data(self, retries=3):
        headers = {
            "User-Agent": "INDEX",
            "Accept": "application/json",
        }
        
        attempt = 0
        while attempt < retries:
            try:
                # Make the API call
                stock_data = self.make_api_call(api_url=constants.ALL_STOCK_MARKET_CAP, headers=headers, timeout=20)
                # Return the data if successful
                return stock_data['data']['rows']
            except Exception as e:
                # Log the exception or print an error (optional)
                print(f"Attempt {attempt + 1} failed: {e}")
                
                # If it's the last attempt, raise the error
                if attempt == retries - 1:
                    raise
                else:
                    # Wait for a short period before retrying (e.g., 2 seconds)
                    time.sleep(2)
            
            attempt += 1
        return stock_data['data']['rows']
    
    def fetch_historical_stock_data(self ,ticker ,go_back_months):
        data = yf.Ticker(ticker)
        stock_data = data.history(period=str(go_back_months) + 'mo')
        return stock_data