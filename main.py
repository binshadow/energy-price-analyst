import sys
import subprocess
from pathlib import Path

from src.orchestration.etl_runner import run_etl


def main() -> None:
    if len(sys.argv) < 2:
        raise ValueError(
            "Usage: python main.py <command> [args]\n"
            "Examples:\n"
            "  python main.py etl\n"
            "  python main.py ui\n"
            "  python main.py test"
        )

    command = sys.argv[1].strip().lower()

    if command == "etl":
        run_etl()

    elif command == "ui":
        run_ui()

    else:
        raise ValueError(f"Unknown command: {command}")


def run_ui() -> None:
    """
    Launches the Streamlit interface.
    """

    project_root = Path(__file__).resolve().parent
    app_path = project_root / "src" / "interface" / "streamlit_app.py"

    print("Launching Streamlit UI...")
    import sys

    subprocess.run(
        [
            sys.executable,  # ← THIS is the key fix
            "-m",
            "streamlit",
            "run",
            str(app_path)
        ],
        cwd=project_root,
    )

if __name__ == "__main__":
    main()