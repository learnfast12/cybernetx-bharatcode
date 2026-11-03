import os, json, urllib.request

BASE_URL = os.environ.get("BHARATCODE_BASE_URL", "https://bharatcode.ai/api/model/v1")
MODEL = os.environ.get("BHARATCODE_MODEL", "qwen-3.8-27b")


def _chat(system, user, max_tokens=250, timeout=15):
    key = os.environ.get("BHARATCODE_API_KEY")
    if not key:
        return None  # no key: caller falls back to template text
    body = json.dumps({
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[bharatcode] call failed: {e}")
        return None


def explain_verdict(url, verdict, signals):
    """ShieldNetX: plain-language reason for a block/warn/allow verdict."""
    text = _chat(
        "You are a security assistant. Explain in 2-3 simple sentences why a link got "
        "this verdict, using only the signals given. Do not invent facts.",
        f"URL: {url}\nVerdict: {verdict}\nSignals: {json.dumps(signals)}",
    )
    return text or f"Verdict: {verdict}. Triggered signals: {', '.join(map(str, signals)) or 'none'}."


def explain_trace(account, findings):
    """TraceNetX: analyst-readable reason an account is suspicious."""
    text = _chat(
        "You are a financial-crime analyst assistant. In 3 short sentences, explain why "
        "this account looks suspicious, using only the findings given. A human analyst "
        "makes the final decision.",
        f"Account: {account}\nFindings: {json.dumps(findings)}",
    )
    return text or f"Account {account} flagged. Findings: {json.dumps(findings)}"
