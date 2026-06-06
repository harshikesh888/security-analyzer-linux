import os
import requests

API_URL = "https://router.huggingface.co/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
    "Content-Type": "application/json"
}

MODEL = "deepseek-ai/DeepSeek-R1"

def analyze(data):

    prompt = f"""
You are an expert Linux SOC (Security Operations Center) analyst.

Analyze the following Arch Linux server security report.

Provide:
1. Suspicious activities detected.
2. Risk Level (LOW/MEDIUM/HIGH/CRITICAL).
3. Possible attack type.
4. Recommended mitigation steps.

Server Report:

{data}

Return a concise security report.
"""

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert cybersecurity analyst."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.2
    }

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json=payload
    )

    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]
