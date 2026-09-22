"""Thin wrapper around the model API.

Talks to OpenRouter through the standard OpenAI client (only `base_url` changes), so
switching to another model means editing the single `MODEL` variable below.
"""
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion

load_dotenv()  # reads OPENROUTER_API_KEY from the .env file

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    # The SDK waits 10 minutes per attempt by default. A free model that stops responding
    # would then look like a frozen program rather than an error, so cap it.
    timeout=60.0,
)

# The only place in the project where a model name appears.
MODEL = "openai/gpt-oss-20b"


def call_llm(system_prompt: str, messages: list, tools: list | None = None) -> ChatCompletion:
    """
    Sends one request to the model and returns the raw response object.

    messages: the conversation so far (user / assistant / tool messages), WITHOUT the system message.
    tools: the tool schemas the model may call (None = plain chat, no tools).
    """
    # Unlike Anthropic's native API, the system prompt is not a separate parameter:
    # it is simply the first message, with role "system".
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    kwargs = {"model": MODEL, "messages": full_messages}
    if tools:
        kwargs["tools"] = tools
        # Temperature 0 makes the model's tool choices as repeatable as possible between runs.
        kwargs["temperature"] = 0

    response = client.chat.completions.create(**kwargs)

    # OpenRouter gotcha: when the upstream model fails or is rate-limited, it answers
    # HTTP 200 with an error payload instead of raising. `choices` is then None, and the
    # caller would crash on choices[0] with an unhelpful TypeError.
    if not response.choices:
        raise RuntimeError(f"{MODEL} returned no answer: {getattr(response, 'error', None) or response}")

    return response
