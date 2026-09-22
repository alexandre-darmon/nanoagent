"""Run logging: one JSON line per model call, appended to logs/run.log.

This is what makes runs comparable (tokens, latency, tools used) without reading the code.
"""
import json
import os
import time


def _parse_arguments(raw: str):
    # Models sometimes return invalid JSON; keep the raw text rather than crash the logger.
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _reasoning_tokens(usage):
    # Not every model reports this, so dig for it defensively rather than assume the shape.
    details = getattr(usage, "completion_tokens_details", None) if usage else None
    return getattr(details, "reasoning_tokens", None) if details else None


def log_turn(iteration: int, tool_calls, usage, latency_s: float, content, log_path="logs/run.log"):
    """
    Records one model call.

    iteration: position in the agent loop (0 = first call)
    tool_calls: the tools the model asked to run (None if it answered with text)
    usage: token counts reported by the API (tokens are the units the model is billed in)
    content: the model's text answer (None when it only asks for tools)
    """
    entry = {
        "timestamp": time.strftime("%m/%d/%Y %H:%M:%S"),
        "iteration": iteration,
        "tools_called": [tc.function.name for tc in (tool_calls or [])],
        # On the OpenAI side, arguments come as a JSON *string*, not a dict.
        "tools_arguments": [_parse_arguments(tc.function.arguments) for tc in (tool_calls or [])],
        "tokens_prompt": usage.prompt_tokens if usage else None,          # what we sent
        "tokens_completion": usage.completion_tokens if usage else None,  # what the model wrote
        # Reasoning models think before answering, and that thinking is billed inside
        # tokens_completion without ever appearing in the answer. Usually the slowest part.
        "tokens_reasoning": _reasoning_tokens(usage),
        "latency_s": round(latency_s, 2),
        "answer": content,
    }
    # logs/ is git-ignored, so it does not exist on a fresh clone.
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

    # The file keeps everything (including long tool arguments); the terminal gets one
    # readable line, so a run reads as a trace instead of a wall of JSON.
    what = ", ".join(entry["tools_called"]) or "answer"
    reasoning = f" ({entry['tokens_reasoning']} reasoning)" if entry["tokens_reasoning"] else ""
    print(f"  [{iteration}] {what} | {entry['tokens_prompt']}→{entry['tokens_completion']} tokens"
          f"{reasoning} | {entry['latency_s']}s")
