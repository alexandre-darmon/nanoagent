# CLAUDE.md

Instructions for Claude Code (or any AI pair-programmer) working on this repo.

## Project

**nanoagent** — a raw agent loop built from scratch, no framework, in the spirit of Karpathy's nanoGPT. It's a portfolio project: the point is to demonstrate a working understanding of what an agent loop actually does before reaching for LangGraph, CrewAI, ADK, etc.

The project is built in eight numbered steps, summarized in the **Steps** table of `README.md` — read it before writing any code. Implement steps in order, and run a manual verification at the end of each one before moving to the next. Don't jump ahead to a later step's logic while implementing an earlier one.

## Non-negotiables

- **No agent framework.** Dependencies are `openai` (for the OpenRouter-compatible client), `python-dotenv`, and `yfinance` (data source for the stock tools). If a task seems to need more, that's a signal to write it by hand, not to add a dependency.
- **OpenRouter via the OpenAI-compatible SDK.** `base_url` swap on the standard `openai` client, not a bespoke HTTP client. The model is a single variable (`MODEL` in `llm.py`) — never hardcode a model name anywhere else, since swapping models with no code change is part of the point.
- **OpenAI function-calling conventions, not Anthropic's native ones.** This project deliberately uses `tools` / `role: "tool"` / `tool_call_id` / `finish_reason == "stop"` — not `tool_use` / `input_schema` / `end_turn`. If you're used to the Anthropic Messages API, don't let those conventions leak in here.
- **Skills are context, not actions.** `load_skill` returns text to be injected into the next message. It must never call an API, write a file, or have any side effect. If you catch yourself giving `load_skill` real side effects, you've turned it into a regular tool and lost the pedagogical point of step 7.
- **Tools with side effects stay fenced.** `write_file` is a real tool, not a skill. It writes only `.md` files inside `reports/` (only the base name of the requested path is kept), and it saves to exactly the name it was given, overwriting if needed. Keep both guarantees if you touch it: the fencing stops the model writing anywhere else, and returning the requested name stops it reading a renamed file as a failure and calling the tool again.
- **No inter-agent communication.** The multi-context pattern (step 6) is an explicit handoff between two separate `run_agent()` calls, each starting from an empty `messages` list. Don't add shared state, a message bus, or anything that lets the two calls "talk" to each other implicitly.

## Code style

- Keep each file single-purpose, matching the structure in `README.md`. Don't merge `tools.py` and `skills.py`, or fold `logger.py` into `main.py`.
- Favor explicit code over abstraction. The value of this repo is that every line is inspectable — no metaclasses, no decorator-based "magic" tool registration. `TOOL_DISPATCH` as a plain dict is intentional; keep it that way.
- Comment the non-obvious parts, especially anywhere OpenRouter/OpenAI diverges from Anthropic's native API (`tool_calls[i].function.arguments` as a JSON string that needs `json.loads()`, message roles, the `finish_reason` check). Those comments are the teaching value of the repo — don't strip them out in a later cleanup pass.
- Every turn goes through `logger.py` (`run.log`): iteration, tools called with their arguments, tokens, latency, and the model's answer. The terminal gets a one-line summary; the file keeps the full entry.

## Implementing a step

1. Implement only what the step asks for.
2. Run a manual test (usually: call the function, print the raw response, inspect it) before continuing to the next step.
3. Never commit `.env` or hardcode `OPENROUTER_API_KEY`.

## Out of scope for this version

Persistent memory across runs, multi-agent orchestration, streaming responses, retry/backoff logic, a formal test suite. If asked to add any of these, say it's out of scope rather than adding it silently — this is a from-scratch learning project, and scope creep defeats the purpose.

## License

MIT (matches nanoGPT's convention).