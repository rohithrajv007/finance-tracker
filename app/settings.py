import json
from pathlib import Path

SETTINGS_PATH = Path(__file__).parent.parent / "data" / "settings.json"
SETTINGS_PATH.parent.mkdir(exist_ok=True)

DEFAULTS = {
    "lm_studio_url":  "http://localhost:1234",
    "model_name":     "phi-3-mini-4k-instruct",
    "theme":          "light",
    "app_version":    "1.0.0",
}


def load() -> dict:
    """Load settings from disk, filling missing keys with defaults."""
    if not SETTINGS_PATH.exists():
        save(DEFAULTS)
        return DEFAULTS.copy()
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # fill any missing keys with defaults
        for k, v in DEFAULTS.items():
            if k not in data:
                data[k] = v
        return data
    except Exception:
        return DEFAULTS.copy()


def save(settings: dict):
    """Save settings to disk."""
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def get(key: str):
    """Get a single setting value."""
    return load().get(key, DEFAULTS.get(key))


def set(key: str, value):
    """Set and save a single setting value."""
    data = load()
    data[key] = value
    save(data)