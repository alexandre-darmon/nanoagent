"""Tools: the actions the model can ask us to run.

Adding a tool takes three edits in this file: its schema (what the model sees), its
function (what actually runs), and its entry in TOOL_DISPATCH (the link between the two).
"""
import json
import math
import os

import yfinance as yf

from skills import load_skill

# What the model sees: a menu of tools, described in the OpenAI function-calling format.
TOOLS_SCHEMA = [
    {
        "type": "function",       # tells the model: "this is a function you can call"
        "function": {
            "name": "get_stock_price",   # the exact name the model uses to call it
            "description": "Get the price of a stock given its ticker",   # the model reads this to decide when to use the tool
            "parameters": {              # the form the model must fill in (JSON Schema)
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
            "name": "get_income_statement",
            "description": "Get the quarterly income statement of a stock given its ticker",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker (e.g., AAPL)"}
                },
                "required": ["ticker"],
            },
        },
    },
    {
        # load_skill only returns text (see skills.py). It is declared like a tool because
        # that is how the model asks for something, but it has no effect on the outside world.
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
    """Turns 94930000000.0 into '94.93B' so large figures are short and readable."""
    # yfinance returns NaN (not None) for missing rows, and NaN would print as "nan".
    if value is None or math.isnan(value):
        return "N/A"
    sign = "-" if value < 0 else ""
    value = abs(value)
    for threshold, suffix in [(1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if value >= threshold:
            return f"{sign}{value / threshold:.2f}{suffix}"
    return f"{sign}{value:.2f}"


def get_stock_price(ticker: str) -> str:
    """Returns the current price of a stock, as a sentence the model can read."""
    stock = yf.Ticker(ticker)
    price = stock.info.get("regularMarketPrice")
    if price is not None:
        return f"The current price of {ticker} stock is {price} USD."
    else:
        return f"Unable to retrieve the price for ticker {ticker}."


def get_income_statement(ticker: str) -> str:
    """Returns revenue and net income for the latest quarter, with the quarter end date."""
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
    # Overwrite, on purpose. An earlier version renamed the file when it already existed, and
    # the model read the unfamiliar path back as a failure and called the tool again — four
    # times in one run, each attempt creating yet another file. A tool that returns something
    # other than what was asked for invites a retry loop; give back the name that was requested.
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Saved {len(content)} characters to {path}."


# Link between a tool's name (what the model says) and the function to run.
TOOL_DISPATCH = {
    "get_stock_price": get_stock_price,
    "get_income_statement": get_income_statement,
    "load_skill": load_skill,
    "write_file": write_file,
}

# Safety net: every tool shown to the model must have a function behind it, and vice versa.
assert {t["function"]["name"] for t in TOOLS_SCHEMA} == set(TOOL_DISPATCH), "TOOLS_SCHEMA and TOOL_DISPATCH are out of sync"


def execute_tool(name: str, arguments_json: str) -> str:
    """
    Runs the tool the model asked for and returns its result as text.
    Errors are returned as text instead of raised, so the model can read them and adapt.
    """
    if name not in TOOL_DISPATCH:
        return f"Unknown tool: {name}"
    try:
        # Unlike Anthropic's native API (where the tool input is already a dict), OpenAI-style
        # tool_calls give the arguments as a JSON *string*, hence json.loads().
        args = json.loads(arguments_json)
        return str(TOOL_DISPATCH[name](**args))
    except Exception as e:
        return f"Error while running {name}: {e}"
