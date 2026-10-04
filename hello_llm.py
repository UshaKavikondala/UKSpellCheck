import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

resp = client.chat.completions.create(
    model="llama3.2",
    messages=[{"role": "user", "content": "Say hi in 3 words"}],
)

print(resp.choices[0].message.content)
print(resp.usage)