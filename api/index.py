"""Vercel serverless entry point for SENTINEL."""

import logging
import sys
from pathlib import Path

# Ensure the parent directory is in the path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from api.app import create_app
    logger.info("Creating SENTINEL Flask app for Vercel...")
    app = create_app()
    logger.info("✓ SENTINEL app initialized successfully")
except ImportError as e:
    logger.error(f"Import error: {e}", exc_info=True)
    raise
except Exception as e:
    logger.error(f"Failed to initialize SENTINEL app: {e}", exc_info=True)
    raise
