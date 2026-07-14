import pathlib
import sys

# Ensure the backend package root is importable so tests can `import main`.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
