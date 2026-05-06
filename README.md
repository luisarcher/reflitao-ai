# python-template

[![CI](https://github.com/luisarcher/python_template/actions/workflows/ci.yml/badge.svg)](https://github.com/luisarcher/python_template/actions/workflows/ci.yml)
[![Release](https://github.com/luisarcher/python_template/actions/workflows/release.yml/badge.svg)](https://github.com/luisarcher/python_template/actions/workflows/release.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A professional Python project template with semantic versioning, CI/CD, linting, type checking, and containerization.

## Features

- Automated semantic versioning and changelog via [python-semantic-release](https://python-semantic-release.readthedocs.io/)
- CI pipeline with linting ([ruff](https://docs.astral.sh/ruff/)), type checking ([ty](https://docs.astral.sh/ty/)), and tests ([pytest](https://pytest.org/))
- Fast dependency management via [uv](https://docs.astral.sh/uv/)
- Container support via `Containerfile` (uv-based)
- All dependencies declared in `pyproject.toml` — no requirements files

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Installation

```bash
uv pip install .
```

## Usage

```bash
app
```

## Development Setup

```bash
# Sync all dev dependencies (creates .venv automatically)
uv sync --group dev

# Run the app
uv run app
```

## Running Tests

```bash
uv run pytest
```

## Linting & Formatting

```bash
uv run ruff check .
uv run ruff format .
```

## Type Checking

```bash
uv run ty check app/
```

## Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) to drive automated versioning:

| Prefix | Effect |
|--------|--------|
| `fix:` | Patch release |
| `feat:` | Minor release |
| `feat!:` / `BREAKING CHANGE` | Major release |

## License

[MIT](LICENSE)
