# nanoagent

A raw agent loop built from scratch — no framework. Just the request/response cycle, function calling, and a lightweight skills system, written in plain Python so every moving part stays visible.

## Why

Most people learn an agent framework before they understand what an agent loop actually is. This project inverts that: build the loop by hand first — the same way [nanoGPT](https://github.com/karpathy/nanoGPT) strips a language model down to its essentials — so that frameworks later become a productivity layer instead of a black box.

## How it works

```mermaid
flowchart LR
    question(["Your question"])
    answer(["Answer"])

    subgraph loop ["The loop"]
        ask["1. Ask the model"]
        decide{"Tool or answer?"}
        run["2. Run the tool"]
        ask --> decide
        decide -->|"tool call"| run
        run -->|"add the result to the conversation"| ask
    end

    question --> ask
    decide -->|"final answer"| answer
```

This is the standard **tool-calling loop** (the "agent loop"): the model decides, we run the tool it asked for, we feed the result back, and it decides again. In ReAct terms, that is reason → act → observe, repeated until the model answers with text instead of a tool call. Every call to the model is also written to `logs/run.log`.

The "tool or answer?" decision reads the response's `finish_reason`:

| `finish_reason` | Meaning | What the loop does |
|---|---|---|
| `tool_calls` | The model wants one or more tools run | Run them, add each result as a `role: "tool"` message, ask again |
| `stop` | The model is done | Return the answer |
| `length` | The answer was cut off (token limit) | Warn and stop |

## What it demonstrates

- **Agent loop** — request → tool_calls → tool execution → re-injection → repeat, until the model signals it's done (`finish_reason == "stop"`)
- **Function calling**, OpenAI-compatible format, via [OpenRouter](https://openrouter.ai) — swap models with one variable, no code changes
- **Skills** — a minimal progressive-disclosure system. Only a skill's name and description sit in the system prompt; the model loads the full instructions on demand via a `load_skill` tool call. Same pattern Claude's own Skills use, reimplemented from first principles
- **Tool vs skill** — `load_skill` only returns text (context, no side effect), while `write_file` really changes the disk, so it is a tool. It never overwrites a report: if the file exists, it adds a timestamp to the name
- **Multi-context handoff** — chaining two agent calls with different system prompts and an explicit handoff between them, not a multi-agent framework

What it deliberately does **not** do: agent-to-agent communication, persistent memory, orchestration graphs. That's a different project.

### What multi-context cost, measured

Both demos answer the same question with the same tools and skills. The only difference is one
context or two.

- **Two contexts cost more.** An earlier measurement put the split at roughly 40% more tokens.
  Treat it as indicative: it ran on another model, and free endpoints vary too much for a single
  percentage to mean much.
- **The handoff is blind.** The second call receives only the text the first produced, never the
  original question — so an error in step one travels to step two unchallenged. We watched a
  failed extraction get faithfully summarised.
- **What it buys** is per-stage logs and a second step with only one job.

**Conclusion: for this task, one context wins.** Splitting pays off when the first stage is far
bigger than the second, or when the stages genuinely need different tools, prompts or models —
none of which is true here. Reach for it when you can name the reason, not by reflex.

### What progressive disclosure costs, measured

Token counts are deterministic, so this part needs no benchmark — it is the `prompt_tokens`
the API reports for each system prompt, with everything else held equal:

| System prompt contains | Tokens | Paid |
|---|---|---|
| The base prompt alone | 97 | — |
| … plus both skill **descriptions** (on-demand) | 192 | **+95, every turn** |
| … plus both full skill **bodies** (upfront) | 363 | **+266, every turn** |

On-demand also pays for the `load_skill` schema (+27 every turn), and once a skill *is* loaded its
body enters the conversation and is re-sent on every later turn (153 tokens for
`income-statement-analysis`, 102 for `stock-report-format`). Counts are tokenizer-specific, so
they move when you change `MODEL`; these were measured on the default above.

So for the run above — 6 turns, both skills loaded early — loading on demand costs **more**
than pasting both skills in from the start. That is the honest result, and it is not a flaw:
a description is worth roughly 40% of its body here, so on-demand only wins once you leave a good
third of your skills unloaded, and it wins bigger the more you leave untouched. Two skills with both
loaded is the worst case for progressive disclosure. It pays off the way it does for Claude's own
Skills: dozens available, one or two used.

## Steps

| Step | What it adds | Where |
|---|---|---|
| 1 | A minimal call to the model through OpenRouter | `llm.py` |
| 2 | A tool declared as a schema | `tools.py` |
| 3 | Tool execution, `role: "tool"` messages, run logging | `tools.py`, `logger.py` |
| 4 | The loop and its stop conditions | `main.py` |
| 5 | A second tool | `tools.py` |
| 6 | Multi-context handoff | `prompts.py`, `main.py` |
| 7 | Skills with progressive loading | `skills.py`, `skills/` |
| 8 | Clean-up and publication | `README.md`, `.env.example` |

## Structure

```
nanoagent/
├── llm.py       # API call wrapper (OpenRouter, OpenAI-compatible)
├── tools.py     # tool schemas + execution (stock price, income statement, load_skill, write_file)
├── skills.py    # skill discovery + loading
├── prompts.py   # system prompts
├── logger.py    # lightweight run logging
├── skills/      # SKILL.md folders
├── logs/        # run.log, one JSON line per model call (created on first run)
├── reports/     # markdown written by the write_file tool (created on first run)
└── main.py      # the loop
```

## Run it

```bash
python --version                  # 3.10 or newer
pip install -r requirements.txt   # openai, python-dotenv, yfinance
cp .env.example .env              # add your OPENROUTER_API_KEY
python main.py                    # one context does the whole job
python main.py multi              # the same question, split over two contexts
```

Each turn prints one line, and the full entry (tool arguments, answer, tokens) goes to `logs/run.log`.
A real run of `python main.py`: the model pulls in the skill it needs to interpret the figures,
fetches them, pulls in the formatting skill, writes the report, and signs off.

```
→ openai/gpt-oss-20b
  [0] load_skill -> income-statement-analysis | 443→64 tokens (37 reasoning) | 0.43s
  [1] get_stock_price -> AAPL | 602→70 tokens (57 reasoning) | 0.56s
  [2] get_income_statement -> AAPL | 649→37 tokens (15 reasoning) | 0.73s
  [3] load_skill -> stock-report-format | 711→113 tokens (106 reasoning) | 0.91s
  [4] write_file -> apple_report.md | 846→810 tokens (634 reasoning) | 4.57s
  [5] answer | 1007→88 tokens (74 reasoning) | 0.85s
```

Nothing in the code decides that order — the model does, one turn at a time, and every turn
re-sends the whole conversation (`tokens_prompt` climbs from 443 to 1007). What five runs across
different models and providers taught us:

- **Tool-calling style differs wildly, and it costs.** `nex-n2.5-pro` fired all four tool calls
  in a single turn and finished in 3 turns (3788 prompt tokens). `gpt-oss-20b` calls one tool per
  turn and needs 6 (4258 prompt tokens). Parallel calls win time *and* tokens, because each extra
  turn re-sends everything before it.
- **Some models never call tools at all.** A 2.6B free model ran the loop happily but **never
  once called `load_skill`**, so every guardrail in the skills silently stopped applying and the
  answer drifted into the investment advice they explicitly forbid. Tool-calling reliability is a
  capability, not a given.
- **The provider is a second dial below the model.** OpenRouter serves one model from many
  providers and picks one per call. Same question, same model: Darkbloom took **18s** and followed
  the skills exactly; sorting by throughput gave CoreWeave and Groq at **8s**, looser. Darkbloom
  also returned an HTTP 400 mid-run and sat behind several five-minute stalls.
- **Thinking is billed but invisible.** Most models here reason before answering, inside
  `tokens_completion` and absent from the reply — 30% of everything generated above, and on one
  free model a single turn spent 1327 of its 1351 tokens thinking, taking 29 seconds.
- **Instruction design beat every code change.** That 1351-token turn was the model re-rendering
  a report it had already written to disk. One sentence added to `skills/stock-report-format/SKILL.md`
  cut it to between 15 and 90 tokens, depending on provider. No code change would have found it.

**In short: the loop is the easy part.** Roughly twenty lines drive it, and they barely changed
across all of this. Everything that actually decided cost, speed and correctness sat outside
them — which model, which provider, and how the instructions were written. That is why `MODEL` is
a single variable and why `logs/run.log` records the model, the provider, the tokens and the
reasoning on every turn: none of the above is visible without it.

## Glossary

For readers new to the vocabulary:

| Term | What it means here |
|---|---|
| **Token** | The unit models read and write, roughly ¾ of a word. Both what you send and what comes back are billed in tokens |
| **System prompt** | The standing instructions sent ahead of the conversation, every single turn |
| **Tool** | A function the model can ask us to run (`get_stock_price`, `write_file`). It *does* something |
| **Skill** | A text file of instructions the model can pull in when relevant. It *says* something, and has no side effect |
| **Context** | Everything the model can see on a given call. A new `run_agent()` call starts with an empty one |

## License

MIT
