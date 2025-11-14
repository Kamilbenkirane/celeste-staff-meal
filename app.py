"""Main entry point for Celeste Staff Meal UI."""

import logging
import sys
from pathlib import Path

# Configure logging to show INFO level logs in Streamlit console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Add src/ to Python path for Streamlit Cloud
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from ui.main import render  # noqa: E402 - Must import after logging config

render()
