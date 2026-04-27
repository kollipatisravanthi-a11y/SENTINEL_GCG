"""Vercel serverless entry point for SENTINEL."""

import logging
import sys
from pathlib import Path

# Ensure the parent directory is in the path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Initializing SENTINEL app for Vercel...")

try:
    from api.app import create_app
    app = create_app()
    logger.info("✓ SENTINEL app initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize SENTINEL app: {e}", exc_info=True)
    # Create a dummy app to prevent startup errors
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return jsonify({"error": f"Failed to initialize app: {str(e)}"}), 500
    
    logger.info("Created error app")
