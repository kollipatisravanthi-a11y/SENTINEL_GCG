#!/usr/bin/env python3
"""Quick test script to verify the app can start up."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    print("Testing SENTINEL app initialization...")
    from api.app import create_app
    
    app = create_app()
    print("✓ Flask app created successfully")
    
    # Test the public key endpoint
    with app.test_client() as client:
        response = client.get('/api/v1/public-key')
        if response.status_code == 200:
            print("✓ Public key endpoint working")
            data = response.get_json()
            if 'public_key_pem' in data and data['public_key_pem']:
                print("✓ Public key loaded correctly")
                print(f"✓ Key starts with: {data['public_key_pem'][:30]}...")
            else:
                print("✗ Public key is empty")
                sys.exit(1)
        else:
            print(f"✗ Public key endpoint failed: {response.status_code}")
            print(f"Response: {response.get_json()}")
            sys.exit(1)
    
    print("\n✅ All tests passed! App is ready for deployment.")
    
except Exception as e:
    print(f"✗ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
