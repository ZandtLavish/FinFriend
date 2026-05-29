from langchain.tools import tool
import yfinance as yf
import requests
import logging

from app.config import settings
from app.schemas import FREDSearchInput, MacroIndicatorInput

logger = logging.getLogger(__name__)

@tool
def get_ticker_price(ticker: str) -> str:
    """
    Get the current stock price for a ticker symbol.
    Input must be a real ticker string e.g. 'AAPL', 'MSFT', 'TSLA'.
    Do not pass a description of the argument — pass the actual ticker.
    
    Information Source: Yahoo Finance
    """
    logger.debug(f"Tool > `get_ticker_price` (ticker: {ticker})")
    
    t = yf.Ticker(ticker)
    try:
        r = t.history()
        candle_l = r.iloc[-1]   # Extract last OHLCV entry (1D)
        candle_prev = r.iloc[-2]
        return f"{ticker}: close=${candle_l['Close']}, volume={candle_l['Volume']}, prev close=${candle_prev['Close']}"
    except Exception as e:
        logger.exception(e)
        return f"Error retrieving price for {ticker}"


@tool(args_schema=FREDSearchInput)
def search_fred_series(query: str, limit: int=3) -> str:
    """
    Search for FRED series IDs matching a description of an economic indicator.
    Use this BEFORE calling get_macro_indicator when you are not certain
    which series_id to use. Returns series IDs with their descriptions.
    """
    r = requests.get(
        "https://api.stlouisfed.org/fred/series/search",
        params={
            "search_text": query,
            "api_key":     settings.FRED_KEY,
            "limit":       limit,
            "file_type":   "json"
        }
    ).json()
    
    results = []
    for s in r.get("seriess", []):
        results.append(
            f"- {s['id']}: {s['title']} "
            f"(freq: {s['frequency_short']}, updated: {s["last_updated"][:10]})"
        )
    
    logger.debug(f"search_fred_series - {results}")
    
    return "\n".join(results) if results else "No matching series found."


@tool(args_schema=MacroIndicatorInput)
def get_macro_indicator(series_id: str) -> str:
    """
    Get the latest value of a macroeconomic indicator from FRED.
    Use this for current values of rates, inflation, employment, growth, and credit spreads.
    Choose the series_id that best matches the user's question from the available options.
    """
    logger.debug(f"Tool > `get_macro_indicator` (series_id: {series_id})")
    
    r = requests.get(
        "https://api.stlouisfed.org/fred/series/observations",
        params={
            "series_id": series_id,
            "api_key": settings.FRED_KEY,
            "limit": 1,
            "sort_order": "desc",
            "file_type": "json"
        }
    )
    
    if r.status_code == 400:
        return(
            f"FRED does not recognize series ID '{series_id}'. "
            "Call search_fred_series to find the correct ID."
        )
    
    obs = r.json()["observations"][0]
    phrase = f"{series_id}: {obs['value']} (as of {obs['date']}). Observed "
    phrase += f"{obs['realtime_start']} - {obs['realtime_end']}." if obs['realtime_start'] != obs['realtime_end'] else f"{obs['realtime_start']}"
    return phrase