import yfinance as yf
import math

TOOLS_SCHEMA = [
    {
        "type": "function",       # ← dit au modèle : "ceci est une fonction que tu peux appeler"
        "function": {
            "name": "get_stock_price",              # ← le nom exact que le modèle utilisera pour t'appeler
            "description": "Get the price of a stock given its ticker",   # ← LA partie la plus importante
            "parameters": {                          # ← le formulaire que le modèle doit remplir
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker (e.g., AAPL)"}
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_income_statement",              # ← le nom exact que le modèle utilisera pour t'appeler
            "description": "Get the quaterly income statement of a stock given its ticker",   # ← LA partie la plus importante
            "parameters": {                          # ← le formulaire que le modèle doit remplir
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker (e.g., AAPL)"}
                },
                "required": ["ticker"],
            },
        },
    }
] 

def format_number(value) -> str:
    """Turn 94930000000.0 into '94.93B'. Handles None/NaN and negatives."""
    if value is None or math.isnan(value):
        return "N/A"
    sign = "-" if value < 0 else ""
    value = abs(value)
    for threshold, suffix in [(1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if value >= threshold:
            return f"{sign}{value / threshold:.2f}{suffix}"
    return f"{sign}{value:.2f}"

def get_stock_price(ticker: str) -> str:
    """
    Récupère le prix d'une action à partir de son ticker.
    """
    stock = yf.Ticker(ticker)
    price = stock.info.get("regularMarketPrice")
    if price is not None:
        return f"The current price of {ticker} stock is {price} USD."
    else:
        return f"Unable to retrieve the price for ticker {ticker}."    

def get_income_statement(ticker: str) -> str:
    stmt = yf.Ticker(ticker).quarterly_income_stmt
    if stmt.empty:
        return f"No income statement found for {ticker}."
    latest = stmt.iloc[:, 0]   # first column = most recent quarter
    revenue = format_number(latest.get("Total Revenue"))
    net_income = format_number(latest.get("Net Income"))
    return f"{ticker} latest quarter: revenue {revenue}, net income {net_income}."


TOOL_DISPATCH = {"get_stock_price": get_stock_price, "get_income_statement": get_income_statement}

def execute_tool(name: str, arguments_json: str) -> str:
    import json
    args = json.loads(arguments_json)
    return str(TOOL_DISPATCH[name](**args))