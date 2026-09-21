# nanoagent

A raw agent loop built from scratch — no LangChain, no LangGraph, no framework. Just the request/response cycle, function calling, and a lightweight skills system, written in plain Python so every moving part stays visible.

## Why

Most people learn an agent framework before they understand what an agent loop actually is. This project inverts that: build the loop by hand first — the same way [nanoGPT](https://github.com/karpathy/nanoGPT) strips a language model down to its essentials — so that frameworks later become a productivity layer instead of a black box.

## What it demonstrates

- **Agent loop** — request → tool_calls → tool execution → re-injection → repeat, until the model signals it's done (`finish_reason == "stop"`)
- **Function calling**, OpenAI-compatible format, via [OpenRouter](https://openrouter.ai) — swap models with one variable, no code changes
- **Skills** — a minimal progressive-disclosure system. Only a skill's name and description sit in the system prompt; the model loads the full instructions on demand via a `load_skill` tool call. Same pattern Claude's own Skills use, reimplemented from first principles
- **Multi-context handoff** — chaining two agent calls with different system prompts and an explicit handoff between them, not a multi-agent framework

What it deliberately does **not** do: agent-to-agent communication, persistent memory, orchestration graphs. That's a different project.

## Structure

```
nanoagent/
├── llm.py       # API call wrapper (OpenRouter, OpenAI-compatible)
├── tools.py     # tool schemas + execution
├── skills.py    # skill discovery + loading
├── prompts.py   # system prompts
├── logger.py    # lightweight run logging
├── skills/      # SKILL.md folders
└── main.py      # the loop
```

## Run it

```bash
pip install openai python-dotenv
cp .env.example .env   # add your OPENROUTER_API_KEY
python main.py
```

## License

MIT