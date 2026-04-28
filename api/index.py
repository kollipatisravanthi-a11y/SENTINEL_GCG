"""Vercel serverless entry point for SENTINEL."""

import logging
import sys
import traceback
from pathlib import Path

# Ensure the parent directory is in the path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import Flask first to ensure it's available
from flask import Flask, jsonify

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Initializing SENTINEL app for Vercel...")

# Initialize app variable before trying to create the real app
app = None
init_error = None

try:
    from api.app import create_app
    app = create_app()
    logger.info("✓ SENTINEL app initialized successfully")
except Exception as e:
    init_error = str(e)
    tb = traceback.format_exc()
    logger.error(f"Failed to initialize SENTINEL app: {e}")
    logger.error(f"Traceback: {tb}")
    
    # Create a fallback app to prevent startup errors
    app = Flask(__name__)
    
    @app.route('/')
    def root():
        return jsonify({
            "status": "initialization_failed",
            "error": init_error,
            "message": "SENTINEL app initialization failed. Check logs for details."
        }), 503
    
    @app.route('/health')
    def health():
        return jsonify({"status": "error", "error": init_error}), 503
    
    @app.route('/<path:path>')
    def catch_all(path):
        return jsonify({
            "status": "initialization_failed",
            "error": init_error,
            "requested_path": path
        }), 503
    
    logger.info("Created fallback error app")
