from llm import call_llm
from tool import TOOLS_SCHEMA, execute_tool
from logger import log_turn
from prompts import PROMPTS
import time

def run_agent(system_prompt: str, user_message: str, tools: list, max_iterations: int = 10) -> list:
    messages = [{"role": "user", "content": user_message}]

    for i in range(max_iterations):
        start = time.time()
        response = call_llm(system_prompt, messages, tools)
        latency = time.time() - start

        choice = response.choices[0]
        log_turn(i, choice.message.tool_calls, response.usage, latency, choice.message.content)

        # "stop" = the model has finished its answer and there are no tool_calls to process.
        if choice.finish_reason == "stop":
            messages.append(choice.message)
            break

        # "length" = the model hit its token limit and was cut off mid-answer.
        # There is no complete tool_calls to process, so stop instead of crashing on None.
        if choice.finish_reason == "length":
            messages.append(choice.message)
            print("⚠️ response truncated (finish_reason == 'length')")
            break

        # otherwise: there are tool_calls to process (step 3b)
        messages.append(choice.message)
        for tool_call in choice.message.tool_calls:
            result = execute_tool(tool_call.function.name, tool_call.function.arguments)
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
    else:
        print("⚠️ max_iterations reached with no conclusion")

    return messages

if __name__ == "__main__":
    question = "What is the price and income statement for Apple, Microsoft and Nvidia stock?"

    # Two contexts: each run_agent() starts from an empty messages list.
    # The only link between them is the text we pass by hand (explicit handoff).
    messages_1 = run_agent(PROMPTS["extraction"], question, TOOLS_SCHEMA)
    extracted = messages_1[-1].content  # last message = assistant object (not a dict) -> .content

    messages_2 = run_agent(PROMPTS["summary"], extracted, [])
    print(messages_2[-1].content)

    # Single context, same job in one prompt: compare its tokens/latency in run.log.
    messages_single = run_agent(PROMPTS["single"], question, TOOLS_SCHEMA)
    print(messages_single[-1].content)
