import yfinance as yf
import math
import os
import skills as s

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
    },
    {
        "type": "function",
        "function": {
            "name": "load_skill",
            "description": "Loads the full instructions of a skill from its name",
            "parameters": {
                "type": "object",
                "properties": {"skill_name": {"type": "string"}},
                "required": ["skill_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Saves text as a markdown (.md) file in the reports folder. Use it only when asked to save or write a report to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "File name only, e.g. apple_report.md"},
                    "content": {"type": "string", "description": "Full markdown content of the file"},
                },
                "required": ["filename", "content"],
            },
        },
    },
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
    quarter_end = stmt.columns[0].strftime("%Y-%m-%d")   # column labels are the period end dates
    revenue = format_number(latest.get("Total Revenue"))
    net_income = format_number(latest.get("Net Income"))
    return f"{ticker} latest quarter (ended {quarter_end}): revenue {revenue}, net income {net_income}."


REPORTS_DIR = "reports"

def write_file(filename: str, content: str) -> str:
    """
    Writes a .md file in REPORTS_DIR. Unlike load_skill, this has a real side effect
    on the disk, which is exactly why it is a tool and not a skill.
    """
    # basename() drops any folder part, so the model cannot write outside REPORTS_DIR ("../x", "/etc/x")
    name = os.path.basename(filename)
    if name.endswith(".md"):
        name = name[:-3]
    if not name:
        return "Invalid filename."
    path = os.path.join(REPORTS_DIR, name + ".md")

    os.makedirs(REPORTS_DIR, exist_ok=True)
    # Never overwrite silently: tell the model so it can pick another name.
    if os.path.exists(path):
        return f"{path} already exists. Choose a different filename."
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Saved {len(content)} characters to {path}."


TOOL_DISPATCH = {"get_stock_price": get_stock_price, "get_income_statement": get_income_statement, "load_skill": s.load_skill, "write_file": write_file}

def execute_tool(name: str, arguments_json: str) -> str:
    import json
    args = json.loads(arguments_json)
    return str(TOOL_DISPATCH[name](**args))