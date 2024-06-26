import os
from together import Together

client = Together(api_key="2e0923315d6b076dade12be49f205ea73836ddee710bcc30365204e4f452c655")

response = client.chat.completions.create(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    messages=[{"role": "user", "content": "Tell me fun things to do in Hong Kong"}],
)
print(response.choices[0].message.content)

#TEST