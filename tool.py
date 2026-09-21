import yfinance as yf

TOOLS_SCHEMA = [
    {
        "type": "function",       # ← dit au modèle : "ceci est une fonction que tu peux appeler"
        "function": {
            "name": "get_stock_price",              # ← le nom exact que le modèle utilisera pour t'appeler
            "description": "Récupère le prix le prix d'un action grace à son ticker",   # ← LA partie la plus importante
            "parameters": {                          # ← le formulaire que le modèle doit remplir
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Identifiant de l'action (Ex: AAPL)"}
                },
                "required": ["ticker"],
            },
        },
    }
] 


def get_stock_price(ticker: str) -> str:
    """
    Récupère le prix d'une action à partir de son ticker.
    """
    stock = yf.Ticker(ticker)
    price = stock.info.get("regularMarketPrice")
    if price is not None:
        return f"Le prix actuel de l'action {ticker} est {price} USD."
    else:
        return f"Impossible de récupérer le prix pour le ticker {ticker}."    

TOOL_DISPATCH = {"get_stock_price": get_stock_price}

def execute_tool(name: str, arguments_json: str) -> str:
    import json
    args = json.loads(arguments_json)
    return str(TOOL_DISPATCH[name](**args))