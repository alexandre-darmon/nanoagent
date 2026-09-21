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
    messages : liste de messages user/assistant/tool (SANS le system)
    Retourne l'objet réponse brut de l'API.
    """
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    kwargs = {"model": model, "messages": full_messages}
    if tools:
        kwargs["tools"] = tools

    response = client.chat.completions.create(**kwargs)
    return response

response = call_llm("Je souhaite récupérer le prix de l'action Apple.", [{"role": "user", "content": "Hello!"}], tool.TOOLS_SCHEMA)
print(response.choices[0].message.content)
print(response.choices[0].message.tool_calls)
