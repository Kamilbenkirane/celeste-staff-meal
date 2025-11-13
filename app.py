"""Main entry point for Celeste Staff Meal UI."""

import logging

# Configure logging to show INFO level logs in Streamlit console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from ui.main import render  # noqa: E402 - Must import after logging config

render()
