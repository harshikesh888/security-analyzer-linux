"""AI analysis backends for the Linux security analyzer.

The backend is selected with the AI_PROVIDER environment variable:

    AI_PROVIDER=huggingface  # default, uses the Hugging Face router
    AI_PROVIDER=ollama       # uses a local or remote Ollama server

See README.md for the full list of configuration variables.
"""

import os

import requests

DEFAULT_HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
DEFAULT_HF_MODEL = "deepseek-ai/DeepSeek-R1"
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.1:8b"

SYSTEM_PROMPT = "You are an expert cybersecurity analyst."


def build_prompt(data):
    return f"""
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


def get_provider():
    return os.getenv("AI_PROVIDER", "huggingface").strip().lower()


def describe_backend():
    """Return a human-readable description of the selected backend."""
    provider = get_provider()

    if provider in ("ollama", "local"):
        model = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
        return f"Ollama ({model} @ {get_ollama_url()})"

    if provider in ("huggingface", "hf", "cloud"):
        model = os.getenv("HF_MODEL", DEFAULT_HF_MODEL)
        return f"Hugging Face ({model})"

    return provider


def get_ollama_url():
    url = os.getenv("OLLAMA_URL") or os.getenv("OLLAMA_HOST") or DEFAULT_OLLAMA_URL
    if "://" not in url:
        url = "http://" + url
    return url.rstrip("/")


def _timeout(default):
    try:
        return float(os.getenv("AI_TIMEOUT", str(default)))
    except ValueError:
        return float(default)


def _temperature():
    try:
        return float(os.getenv("AI_TEMPERATURE", "0.2"))
    except ValueError:
        return 0.2


def _max_tokens():
    try:
        return int(os.getenv("AI_MAX_TOKENS", "500"))
    except ValueError:
        return 500


def _ollama_num_ctx():
    try:
        return int(os.getenv("OLLAMA_NUM_CTX", "8192"))
    except ValueError:
        return 8192


def _analyze_with_huggingface(prompt):
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError(
            "HF_TOKEN is not set. Export a Hugging Face token or set "
            "AI_PROVIDER=ollama to use a local model."
        )

    url = os.getenv("HF_API_URL", DEFAULT_HF_API_URL)
    model = os.getenv("HF_MODEL", DEFAULT_HF_MODEL)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": _max_tokens(),
        "temperature": _temperature(),
    }

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=_timeout(120),
    )
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


def _analyze_with_ollama(prompt):
    base_url = get_ollama_url()
    model = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    url = f"{base_url}/api/chat"

    headers = {"Content-Type": "application/json"}
    api_key = os.getenv("OLLAMA_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": _temperature(),
            "num_predict": _max_tokens(),
            "num_ctx": _ollama_num_ctx(),
        },
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=_timeout(600),
        )
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {base_url}. Start it with "
            "'ollama serve' or set OLLAMA_URL to the correct address."
        ) from exc

    response.raise_for_status()

    return response.json()["message"]["content"]


def analyze(data):
    prompt = build_prompt(data)
    provider = get_provider()

    if provider in ("ollama", "local"):
        return _analyze_with_ollama(prompt)

    if provider in ("huggingface", "hf", "cloud"):
        return _analyze_with_huggingface(prompt)

    raise ValueError(
        f"Unknown AI_PROVIDER '{provider}'. "
        "Use 'huggingface' or 'ollama'."
    )
