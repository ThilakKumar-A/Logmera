import os
import json
from typing import Any
from pathlib import Path
import requests

DEFAULT_TIMEOUT_SECONDS = 10
DEFAULT_RETRIES = 2

CONFIG_DIR = Path.home() / ".logmera"
CONFIG_FILE = CONFIG_DIR / "config.env"


def _read_saved_url() -> str | None:
    if not CONFIG_FILE.exists():
        return None

    for line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("LOGMERA_URL="):
            value = stripped.split("=", 1)[1].strip()
            if value:
                return value.strip("\"'")
    return None


def _get_int_env(name: str, default: int, min_value: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        os.environ[name] = str(default)
        return default
    try:
        value = int(raw)
    except ValueError:
        os.environ[name] = str(default)
        return default
    if value < min_value:
        os.environ[name] = str(default)
        return default
    return value

def _base_url() -> str:
    # Try to read from config file first
    value = _read_saved_url()
    
    # If not in config, try environment variable
    if not value:
        value = os.getenv("LOGMERA_URL")
    
    # If still no value, use default
    if not value or not value.strip():
        return "http://127.0.0.1:8000"
    
    return value.rstrip("/")


def _format_send_error(error: Exception) -> str:
    url = _base_url()
    if isinstance(error, requests.exceptions.ConnectionError):
        return (
            f"Could not connect to Logmera at {url}. "
            "Start the backend with `logmera --port 8000 --db-url <postgres-url>` "
            "(or set LOGMERA_URL to the correct server)."
        )
    return str(error)


def _coerce_text(value: Any) -> str:
    """Convert any value to a stable string for log payloads."""
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        return json.dumps(value, default=str)
    if isinstance(value, (list, tuple, set)):
        return json.dumps(list(value), default=str)

    # Handle rich SDK/LLM response objects safely.
    text_attr = getattr(value, "text", None)
    if isinstance(text_attr, str) and text_attr:
        return text_attr

    if hasattr(value, "model_dump"):
        try:
            return json.dumps(value.model_dump(), default=str)
        except Exception:
            pass

    if hasattr(value, "dict"):
        try:
            return json.dumps(value.dict(), default=str)
        except Exception:
            pass

    return str(value)


def log(
    project_id: Any,
    prompt: Any,
    response: Any,
    model: Any,
    latency_ms: int | None = None,
    status: Any = None,
) -> bool:
    """Send one observability log to Logmera."""
    project_id_text = _coerce_text(project_id)
    prompt_text = _coerce_text(prompt)
    response_text = _coerce_text(response)
    model_text = _coerce_text(model)
    status_text = _coerce_text(status) if status is not None else None

    payload = {
        "project_id": project_id_text,
        "prompt": prompt_text,
        "response": response_text,
        "model": model_text,
        "latency_ms": latency_ms,
        "status": status_text,
    }

    required = ("project_id", "prompt", "response", "model")
    missing = [key for key in required if not payload[key]]
    if missing:
        raise ValueError(f"Missing required log fields: {', '.join(missing)}")

    timeout = _get_int_env(
        "LOGMERA_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS, min_value=10
    )
    retries = _get_int_env("LOGMERA_RETRIES", DEFAULT_RETRIES, min_value=1)
    url = f"{_base_url()}/logs"
    last_error: Exception | None = None
    for _ in range(retries + 1):
        try:
            resp = requests.post(url, json=payload, timeout=timeout)
            resp.raise_for_status()
            return True
        except Exception as exc:  
            last_error = exc

    if last_error is not None:
        print(f"[logmera-sdk] failed to send log: {_format_send_error(last_error)}")
    else:
        print("[logmera-sdk] failed to send log: unknown error")
    return False
