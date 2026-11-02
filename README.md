# Linux Security Analyzer

A Python tool that takes a snapshot of a Linux host's security state and asks an LLM
to analyze it. It collects system usage, failed logins, the firewall ruleset hash,
running processes, listening ports, hashes of critical files, services, users, and
cron jobs, prints the report as JSON, and returns a SOC-style assessment with
findings, risk level, and mitigations.

Two AI backends are available:

- **Hugging Face** (default) — a hosted model; the report is sent to Hugging Face.
- **Ollama** — a local model; the report stays on your machine.

## Requirements

- Linux with systemd (`journalctl`)
- Python 3.8+
- `psutil` and `requests`
- `nftables` for the firewall check (optional)
- Root privileges for complete results (`/etc/shadow`, `/etc/sudoers`, the full
  journal, and `nft`)

## Install

```bash
cd security-analyzer-linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Use with Hugging Face

Create a token at <https://huggingface.co/settings/tokens>, then run:

```bash
export HF_TOKEN="hf_..."
sudo -E .venv/bin/python main.py
```

## Use with local Ollama

Install Ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Download a model and make sure the server is running:

```bash
ollama pull llama3.1:8b
ollama serve            # skip if the systemd service is already running
```

Run the analyzer against Ollama:

```bash
export AI_PROVIDER=ollama
export OLLAMA_MODEL=llama3.1:8b
export OLLAMA_URL=http://localhost:11434
sudo -E .venv/bin/python main.py
```

Other models that work well include `llama3.2:3b` (faster, lower memory),
`qwen2.5:7b`, and `deepseek-r1:8b`. For a remote Ollama server, set `OLLAMA_URL` to
its address, e.g. `http://192.168.1.50:11434`.

## Configuration

All options are environment variables:

| Variable | Default | Description |
|---|---|---|
| `AI_PROVIDER` | `huggingface` | `huggingface` or `ollama` |
| `HF_TOKEN` | — | Hugging Face API token (required for Hugging Face) |
| `HF_MODEL` | `deepseek-ai/DeepSeek-R1` | Hugging Face model |
| `HF_API_URL` | `https://router.huggingface.co/v1/chat/completions` | Hugging Face endpoint |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL (`OLLAMA_HOST` also works) |
| `OLLAMA_MODEL` | `llama3.1:8b` | Model name from `ollama list` |
| `OLLAMA_NUM_CTX` | `8192` | Ollama context window |
| `OLLAMA_API_KEY` | — | Optional bearer token for an authenticating proxy |
| `AI_TIMEOUT` | `120` (Hugging Face), `600` (Ollama) | Request timeout in seconds |
| `AI_TEMPERATURE` | `0.2` | Sampling temperature |
| `AI_MAX_TOKENS` | `500` | Maximum response tokens |

Use `sudo -E` so the analyzer keeps these variables when it runs as root. The
selected backend is printed above the analysis.
