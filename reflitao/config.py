import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "reflitao"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_SESSION = "session0"
DEFAULT_LLM_MODEL = "claude-sonnet-4-6"


@dataclass
class Config:
    telegram_token: str
    openai_api_key: str
    anthropic_api_key: str
    sessions_dir: Path
    state_file: Path


def load_config(data_dir: Path) -> Config:
    """Load config from env vars (highest priority) then XDG config file."""
    file_cfg: dict = {}

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "rb") as f:
            raw = tomllib.load(f)
        file_cfg = raw.get("keys", {})

    def _get(env_var: str, file_key: str) -> str:
        val = os.environ.get(env_var) or file_cfg.get(file_key)
        if not val:
            print(
                f"Error: {env_var} not set and '{file_key}' not found in {CONFIG_FILE}\n"
                f"Run 'reflitao init' to configure, or set the environment variable.",
                file=sys.stderr,
            )
            sys.exit(1)
        return val

    return Config(
        telegram_token=_get("REFLITAO_TELEGRAM_TOKEN", "telegram_token"),
        openai_api_key=_get("REFLITAO_OPENAI_API_KEY", "openai_api_key"),
        anthropic_api_key=_get("REFLITAO_ANTHROPIC_API_KEY", "anthropic_api_key"),
        sessions_dir=data_dir / "sessions",
        state_file=data_dir / "state.json",
    )


def init_config() -> None:
    """Interactive first-time configuration."""
    print("reflitão — first-time setup\n")

    telegram_token = input("Telegram bot token: ").strip()
    openai_api_key = input("OpenAI API key: ").strip()
    anthropic_api_key = input("Anthropic API key: ").strip()

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    content = (
        "[keys]\n"
        f'telegram_token = "{telegram_token}"\n'
        f'openai_api_key = "{openai_api_key}"\n'
        f'anthropic_api_key = "{anthropic_api_key}"\n'
    )

    CONFIG_FILE.write_text(content, encoding="utf-8")
    print(f"\nConfig saved to {CONFIG_FILE}")
