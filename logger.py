import json, time

def log_turn(iteration: int, tool_calls, usage, latency_s: float, content, log_path="logs/run.log"):
    
    entry = {
        "timestamp": time.strftime("%m/%d/%Y %H:%M:%S"),
        "iteration": iteration,
        "tools_called": [tc.function.name for tc in (tool_calls or [])],
        # arguments is a JSON *string* on the OpenAI side, so json.loads() it to log a real dict
        "tools_arguments": [json.loads(tc.function.arguments) for tc in (tool_calls or [])],
        "tokens_prompt": usage.prompt_tokens if usage else None,
        "tokens_completion": usage.completion_tokens if usage else None,
        "latency_s": round(latency_s, 2),
        # message.content is None when the model only emits tool_calls
        "answer": content,
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(entry)  # visible directly, in addition to the file