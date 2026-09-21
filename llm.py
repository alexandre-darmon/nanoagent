from openai import OpenAI
import os
from dotenv import load_dotenv
import tool


load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

model = "nex-agi/nex-n2.5-mini:free"
# llm.py
def call_llm(system_prompt: str, messages: list, tools: list = None) -> dict:
    """
    messages : list of messages (user/assistant/tool) (WITHOUT the system message)
    Returns the raw API response object.
    """
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    kwargs = {"model": model, "messages": full_messages}
    if tools:
        kwargs["tools"] = tools
        kwargs["temperature"] = 0

    response = client.chat.completions.create(**kwargs)
    return response
