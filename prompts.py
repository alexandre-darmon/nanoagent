"""System prompts: the standing instructions given to the model at the start of each run."""

PROMPTS = {
    # Context 1: only gathers raw data with the tools, no interpretation.
    # Say what to produce, not what to refuse: a blanket "do not summarize" collides with a
    # question that asks for a summary, and the model answers "I can't comply with that".
    "extraction": "You extract the key financial data for the requested company only using the available tools, no memory answer. Report the figures you collected, without interpreting them.",
    # Context 2: summarizes the text it receives, and owns producing the report file.
    "summary": "You summarize in 3 points maximum, factual tone, then save the result as a markdown report.",
    # Does the whole job in one context: the 1-context side of the comparison.
    "single": "You extract the key financial data for the requested company using the available tools, then summarize it in 3 points maximum, factual tone.",
}
