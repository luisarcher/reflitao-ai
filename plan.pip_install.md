# Plan: Make reflitão pip-installable with proper user configuration

## Summary

Restructure the project so that `reflitao` is the root Python package, installable via `pip install reflitao`. The bot runs with `python -m reflitao [dir]` where `dir` defaults to `.`. Sessions and state are stored in the working directory. Configuration (API keys) lives in `~/.config/reflitao/config.toml`, not `.env`.

---

## Configuration Pattern: XDG + Environment Override

After `pip install reflitao`, the user experience is:

```bash
# First-time setup — interactive prompt creates config file
reflitao init

# This creates ~/.config/reflitao/config.toml:
# [keys]
# telegram_token = "..."
# openai_api_key = "..."
# anthropic_api_key = "..."

# Run the bot (sessions stored in current directory)
reflitao

# Or specify a workspace directory
reflitao ~/my-thinking-sessions
```

**Resolution order** (highest priority first):
1. Environment variables (`REFLITAO_TELEGRAM_TOKEN`, etc.) — for containers/CI
2. Config file at `$XDG_CONFIG_HOME/reflitao/config.toml` (default `~/.config/reflitao/config.toml`)

**Why this over `.env`:**
- Config is global per-user, not per-directory (API keys don't change per session)
- No need to copy `.env` into every project
- Environment variables still work for Docker/CI
- `reflitao init` gives a guided first-run experience

---

## Package Structure (target)

```
reflitao/
├── __init__.py             # __version__
├── __main__.py             # Entry: python -m reflitao [dir]
├── config.py               # XDG config loading + env override
├── bot.py                  # Application builder, handler registration
├── handlers/
│   ├── __init__.py
│   ├── session_cmd.py
│   ├── text_msg.py
│   ├── media.py
│   ├── prompt_cmd.py
│   ├── get_cmd.py
│   └── image_cmd.py
└── services/
    ├── __init__.py
    ├── whisper.py
    ├── llm.py
    └── image.py
```

---

## Phases

### Phase 1 — Restructure into `reflitao/` package
1. Move `bot.py` → `reflitao/bot.py`
2. Move `config.py` → `reflitao/config.py` (rewrite for XDG pattern)
3. Move `handlers/` → `reflitao/handlers/`
4. Move `services/` → `reflitao/services/`
5. Create `reflitao/__main__.py` — parses optional `[dir]` argument, sets working dir, runs bot
6. Delete top-level `bot.py`, `config.py`, old `handlers/`, old `services/`
7. Fix all internal imports to use `reflitao.` prefix

### Phase 2 — Config rewrite (`reflitao/config.py`)
8. Use `tomllib` (stdlib 3.11+) to read `~/.config/reflitao/config.toml`
9. Environment variables override: `REFLITAO_TELEGRAM_TOKEN`, `REFLITAO_OPENAI_API_KEY`, `REFLITAO_ANTHROPIC_API_KEY`
10. Expose `load_config() -> Config` dataclass with all settings
11. `SESSIONS_DIR` and `STATE_FILE` are relative to the runtime working directory (the `[dir]` arg)

### Phase 3 — `reflitao init` command
12. Add a CLI entry point `reflitao` that dispatches subcommands: `reflitao init`, `reflitao` (no subcommand = run bot)
13. `reflitao init` — prompts user for each key, writes `~/.config/reflitao/config.toml`
14. On bot start, if config is missing, print a helpful error pointing to `reflitao init`

### Phase 4 — Persist AI responses
15. In `/promptsession` and `/prompt` handlers, after getting the LLM response, save it as `YYYYMMDDHHMMSS_response.md` in the current session folder
16. Format: include the prompt as a header, then the response body

### Phase 5 — pyproject.toml for publishing
17. Update `pyproject.toml`:
    - `[project.scripts]`: `reflitao = "reflitao.__main__:main"`
    - Remove `python-dotenv` from dependencies (no longer needed)
    - Add `tomli` for Python <3.11 compat (or require 3.11+ and use `tomllib`)
    - Proper metadata: description, classifiers, URLs
18. Remove `.env.example` (replaced by `reflitao init`)

### Phase 6 — CI/CD for PyPI publishing
19. Add `.github/workflows/publish.yml`:
    - Trigger: on tag push (`v*`) or GitHub Release
    - Steps: checkout → setup Python → install `build` → `python -m build` → `twine upload` using `PYPI_TOKEN` secret
    - Or use trusted publishing (recommended): `pypa/gh-action-pypi-publish`
20. The existing CI workflow should run tests/lint on PRs

---

## Publishing to PyPI — Steps

1. **Register on PyPI**: Create account at pypi.org
2. **Configure trusted publishing** (recommended): In PyPI project settings, add GitHub as a trusted publisher (repo + workflow file)
3. **Tag a release**: `git tag v0.1.0 && git push --tags`
4. **CI builds and publishes**: The workflow builds the sdist+wheel and uploads via trusted publishing (no token needed if configured)

Alternative (manual):
```bash
uv run python -m build
uv run twine upload dist/*  # needs ~/.pypirc or PYPI_TOKEN
```

---

## User Workflow (final)

```bash
# Install
pip install reflitao          # or: uv pip install reflitao

# Configure (one-time)
reflitao init
# → Enter Telegram token: ...
# → Enter OpenAI API key: ...
# → Enter Anthropic API key: ...
# → Config saved to ~/.config/reflitao/config.toml

# Run (sessions stored in current dir)
cd ~/notes
reflitao                      # creates ./sessions/ and ./state.json here

# Or equivalently:
python -m reflitao ~/notes
```

---

## Decisions

- **XDG config over .env** — keys are user-global, not project-specific; survives across directories
- **Working directory = data root** — sessions/state are local to where you run, enabling per-project thinking spaces
- **`python -m reflitao` support** — standard Python package convention
- **`reflitao init`** — friendly onboarding, no manual file editing needed
- **Environment variable override** — critical for Docker/CI deployment
- **Require Python 3.11+** — use stdlib `tomllib`, no extra dependency
- **Persist AI responses** — every LLM interaction is captured as part of the session record
- **Read-only install** — the package itself is pure code; all mutable state goes to working dir or XDG config


______

Additional comments:
bro, you can fucking use uv build and uv publish, can't you?!

also tell me more about pypa/gh-action-pypi-publish
I've never published a project to pypi

