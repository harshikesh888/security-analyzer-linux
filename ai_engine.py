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

Analyze the following Arch Linux security report.

Analysis rules:
- Linux kernel worker threads (kworker, kthreadd, rcu_*, cpuhp, migration) are normal.
- Ports bound to 127.0.0.1, ::1, or ::ffff:127.0.0.1 are localhost-only and should not be treated as externally exposed.
- Port 631 (CUPS/IPP) is a legitimate local printing service.
- Port 63342 is commonly used by JetBrains IDEs (PyCharm/IntelliJ) and is legitimate when localhost-only.
- If /etc/shadow or /etc/sudoers show "ERROR", assume this may simply indicate insufficient permissions unless other evidence suggests tampering.
- Empty failed_logins means no authentication attacks were detected.
- Enabled bluetooth.service should be treated as a minor hardening recommendation, not an active threat.
- Unknown services listening on non-localhost interfaces should be considered suspicious.

Provide:

1. Suspicious activities detected.
2. Overall risk level (LOW/MEDIUM/HIGH/CRITICAL).
3. Possible attack type (if any).
4. Recommended mitigation steps.
5. A one-sentence overall verdict.

Keep the report concise and avoid false positives.

Server Report:

{data}
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
