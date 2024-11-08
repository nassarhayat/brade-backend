import requests

def get_stock_data(stock_symbol: str):
  print(stock_symbol, "STOCKS")
  # url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stock_symbol}&interval=30min&apikey=TZK18T0IBOMJ1ER6"
  url = f"https://api.polygon.io/v2/aggs/ticker/{stock_symbol}/range/1/day/2023-01-09/2023-02-10?adjusted=true&sort=asc&apiKey=TndcqjQp6CyeueFJmsPXnpF7PIbH62_2"
  r = requests.get(url)
  data = r.json()
  # print("data", data)
  stock_ticker = data["ticker"]
  time_series_data = data["results"]
  return { 
    "stock_ticker": stock_ticker, 
    "time_series_data": time_series_data 
  }