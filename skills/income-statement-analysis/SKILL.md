---
name: income-statement-analysis
description: How to interpret a company's quarterly revenue and net income (margins, comparisons, caveats). Use when asked to analyze, compare or judge a company's profitability.
---

You have raw figures from `get_income_statement` (revenue, net income for the latest quarter).
Turn them into an analysis using these rules:

1. Compute the net margin: net income / revenue, as a percentage with one decimal.
2. When comparing companies, rank them by net margin first, then by revenue. Say which is
   bigger in absolute terms and which is more profitable relative to its size.
3. Always state the quarter end date returned by the tool. Never call a single quarter a "trend".
4. A high margin does not mean a good investment. Do not give buy/sell advice.
5. If a figure is missing or "N/A", say so. Never estimate it from memory.
