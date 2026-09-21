PROMPTS = {
    # Context 1: only gathers raw data with the tools, no interpretation.
    "extraction": "You extract the key financial data for the requested company only using the available tools, no memory answer.",
    # Context 2: only writes the summary from the text it receives.
    "summary": "You summarize in 3 points maximum, factual tone.",
    # One-size-fits-all version, used only to compare tokens and logs against the 2-call version.
    "single": "You extract the key financial data for the requested company using the available tools, then summarize it in 3 points maximum, factual tone.",
}
