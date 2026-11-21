import sys
from pathlib import Path

# let the tests run without installing the package first
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
