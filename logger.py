import time, json

def log_turn(iteration: int, tool_calls, usage, latency_s: float, log_path="run.log"):
    entry = {
        "iteration": iteration,
        "tools_called": [tc.function.name for tc in (tool_calls or [])],
        "tokens_prompt": usage.prompt_tokens if usage else None,
        "tokens_completion": usage.completion_tokens if usage else None,
        "latency_s": round(latency_s, 2),
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(entry)  # visible directly, in addition to the file