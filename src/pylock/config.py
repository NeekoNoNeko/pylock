import json
import os
import sys
from pathlib import Path


DEFAULT_CONFIG_PATH = "config.json"


def get_program_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


def ensure_config_exists(config_path: str | Path = DEFAULT_CONFIG_PATH) -> Path:
    config_path = Path(config_path)
    program_dir = get_program_dir()
    full_path = program_dir / config_path

    if not full_path.exists():
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump({"password": ""}, f, ensure_ascii=False, indent=4)

    return full_path


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict:
    config_path = ensure_config_exists(config_path)

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_password(config_path: str = DEFAULT_CONFIG_PATH) -> str:
    config = load_config(config_path)
    return config.get("password", "")
