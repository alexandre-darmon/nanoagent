"""System prompts: the standing instructions given to the model at the start of each run."""

PROMPTS = {
    # Context 1: only gathers raw data with the tools, no interpretation.
    "extraction": "You extract the key financial data for the requested company only using the available tools, no memory answer.",
    # Context 2: only writes the summary from the text it receives.
    "summary": "You summarize in 3 points maximum, factual tone.",
    # Does the whole job in one context: the 1-context side of the comparison.
    "single": "You extract the key financial data for the requested company using the available tools, then summarize it in 3 points maximum, factual tone.",
}
