from llm import call_llm
from tool import TOOLS_SCHEMA, execute_tool


assistant_message = response.choices[0].message
print(assistant_message.content)
messages.append(assistant_message)  # important: re-inject the assistant message as-is (it contains the tool_calls)
print(messages)

for tool_call in assistant_message.tool_calls:
    result = execute_tool(tool_call.function.name, tool_call.function.arguments)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result,
    })