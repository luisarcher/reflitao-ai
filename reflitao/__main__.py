import sys
from pathlib import Path

from reflitao.config import init_config


def main() -> None:
    args = sys.argv[1:]

    # Handle 'init' subcommand
    if args and args[0] == "init":
        init_config()
        return

    # Determine data directory
    data_dir = Path(args[0]).resolve() if args else Path.cwd()

    # Ensure data dir exists
    data_dir.mkdir(parents=True, exist_ok=True)

    # Import and run bot (deferred so config loads only when needed)
    from reflitao.bot import run_bot

    run_bot(data_dir)


if __name__ == "__main__":
    main()
