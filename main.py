import sys

from src.orchestration.etl_runner import run_etl
from src.ai.analyst import ask_question


def main() -> None:
    if len(sys.argv) < 2:
        raise ValueError(
            "Usage: python main.py <command> [args]\n"
            "Examples:\n"
            "  python main.py etl\n"
            "  python main.py ask \"summarize prices\"\n"
            "  python main.py ask \"show top price spikes\""
        )

    command = sys.argv[1].strip().lower()

    if command == "etl":
        run_etl()

    elif command == "ask":
        question = " ".join(sys.argv[2:])

        if not question:
            raise ValueError(
                "Please provide a question.\n"
                "Example: python main.py ask \"summarize prices\""
            )

        ask_question(question)

    else:
        raise ValueError(f"Unknown command: {command}")


if __name__ == "__main__":
    main()