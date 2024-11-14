import os
import requests
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("POLYGON_API_KEY")

def get_stock_aggregates(
  stock_symbol: str,
  multiplier: int = 1,
  timespan: str = "day",
  from_date: str = "2023-01-09",
  to_date: str = "2023-02-10"
):
  """
  Get aggregate bars for a stock over a given date range in custom time window sizes.
  """
  url = f"https://api.polygon.io/v2/aggs/ticker/{stock_symbol}/range/{multiplier}/{timespan}/{from_date}/{to_date}?adjusted=true&sort=asc&apiKey={API_KEY}"
  r = requests.get(url)
  data = r.json()
  print("DATA", data)
  return { 
    "stock_ticker": data["ticker"], 
    "time_series_data": data["results"] 
  }

def get_fx_aggregates(
  fx_symbol: str,
  multiplier: int = 1,
  timespan: str = "day",
  from_date: str = "2023-01-09",
  to_date: str = "2023-02-10"
):
  """
  Get aggregate bars for a forex pair over a given date range in custom time window sizes.
  """
  url = f"https://api.polygon.io/v2/aggs/ticker/{fx_symbol}/range/{multiplier}/{timespan}/{from_date}/{to_date}?adjusted=true&sort=asc&apiKey={API_KEY}"
  r = requests.get(url)
  data = r.json()
  return { 
    "fx_ticker": data["ticker"], 
    "time_series_data": data["results"] 
  }
