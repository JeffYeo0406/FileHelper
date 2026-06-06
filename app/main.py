from pathlib import Path
import sys


backend_dir = Path(__file__).resolve().parent.parent / "backend"
backend_path = str(backend_dir)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app  # noqa: E402
