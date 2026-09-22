"""The agent loop, plus two runnable demos of the same question.

Usage:
    python main.py          # one context does the whole job
    python main.py multi    # the same question, split over two contexts
"""
import sys
import time

from llm import MODEL, call_llm
from logger import log_turn
from prompts import PROMPTS
from skills import discover_skills
from tools import TOOLS_SCHEMA, execute_tool


def run_agent(system_prompt: str, user_message: str, tools: list, max_iterations: int = 10) -> list:
    """
    Runs the agent on one question and returns the full conversation (list of messages).

    The model cannot run code itself. When it needs data, it answers with a "tool call"
    (a request to run one of our functions). We run it, send the result back, and ask
    again. The loop ends when the model answers with text instead of a tool call.
    max_iterations is a safety limit in case the model never stops asking for tools.
    """
    # `messages` is the conversation memory: the model only knows what is in this list.
    messages = [{"role": "user", "content": user_message}]

    # Nothing is printed until the first reply arrives, and on a busy free endpoint that can
    # be half a minute. Say who we are waiting on, so a slow run is not mistaken for a hung one.
    print(f"→ {MODEL}", flush=True)

    for i in range(max_iterations):
        start = time.time()
        response = call_llm(system_prompt, messages, tools)
        latency = time.time() - start

        choice = response.choices[0]
        # response.model is what actually answered, which is not always what we asked for:
        # OpenRouter may route elsewhere. Log that rather than our own MODEL constant.
        log_turn(i, choice.message.tool_calls, response.usage, latency, choice.message.content, response.model)

        # Keep the model's message as-is in the history: when it asks for tools it carries the
        # tool_calls, and each tool result below must point back to one of them.
        messages.append(choice.message)

        # "length" = the model hit its token limit and was cut off mid-answer.
        if choice.finish_reason == "length":
            print("⚠️ response truncated (finish_reason == 'length')")
            break

        # No tool calls means there is nothing left to run, so the turn is the final answer.
        # Drive the loop off tool_calls rather than off finish_reason: "stop" is the normal
        # case, but providers also return values of their own ("error", "content_filter"...),
        # and treating those as tool calls would crash on `for tool_call in None`.
        if not choice.message.tool_calls:
            if choice.finish_reason != "stop":
                print(f"⚠️ stopped on finish_reason={choice.finish_reason!r} with no tool calls")
            break

        for tool_call in choice.message.tool_calls:
            result = execute_tool(tool_call.function.name, tool_call.function.arguments)
            # Unlike Anthropic (tool result inside a "user" message), OpenAI uses a separate
            # message with role "tool", linked to the request by tool_call_id.
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
    else:
        # for/else: runs only when the loop ended without a break.
        print("⚠️ max_iterations reached with no conclusion")

    return messages


def build_system_prompt(base_prompt: str) -> str:
    """Adds the list of available skills (name + description only) to the base prompt."""
    skills = discover_skills()
    if not skills:
        return base_prompt
    summary = "\n".join(f"- {s['name']}: {s['description']}" for s in skills)
    return (
        f"{base_prompt}\n\n"
        f"Available skills (use `load_skill` to load the full instructions "
        f"before applying them):\n{summary}"
    )


def final_answer(messages: list) -> str:
    """
    The model's last reply. Messages we build ourselves are dicts, messages coming back
    from the model are objects — so a dict here means the loop stopped on a tool result
    (max_iterations) rather than on an answer.
    """
    last = messages[-1]
    if isinstance(last, dict):
        return "(no final answer: the loop stopped on a tool result)"
    # `content` is None whenever the model ends a turn without writing any text. Returning it
    # raw would hand None to the next context, and the API rejects a message with null content.
    return last.content or "(no final answer: the model returned no text)"


# Both demos answer this exact question, so the only thing that differs between them
# is the number of contexts. Same question, same tools, same skills.
QUESTION = (
    "What is the price and income statement for Apple stock? Interpret the results "
    "and summarize it. Then write a report in markdown format and save it to a file "
    "named apple_report.md."
)


def demo_single() -> None:
    """One context does the whole job: load skills, call the data tools, write the report."""
    messages = run_agent(build_system_prompt(PROMPTS["single"]), QUESTION, TOOLS_SCHEMA)
    print(final_answer(messages))


def demo_multi_context() -> None:
    """
    The same job split over two contexts: one extracts, one summarizes.

    Each run_agent() starts from an empty messages list, so the second call knows nothing
    except the text we hand it — that is the explicit handoff, and the reason a mistake in
    the first step travels to the second unnoticed.
    """
    messages_1 = run_agent(build_system_prompt(PROMPTS["extraction"]), QUESTION, TOOLS_SCHEMA)
    extracted = final_answer(messages_1)

    messages_2 = run_agent(build_system_prompt(PROMPTS["summary"]), extracted, TOOLS_SCHEMA)
    print(final_answer(messages_2))


DEMOS = {"single": demo_single, "multi": demo_multi_context}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "single"   # python main.py [single|multi]
    if mode not in DEMOS:
        sys.exit(f"Unknown mode '{mode}'. Use one of: {', '.join(DEMOS)}")
    DEMOS[mode]()
