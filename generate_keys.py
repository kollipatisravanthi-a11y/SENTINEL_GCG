#!/usr/bin/env python3
"""Generate RSA keys and output them as base64 for use as Vercel environment variables."""

import base64
import sys
from pathlib import Path

# Add parent directory to path to import api modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

from api.crypto.rsa_engine import generate_private_key, serialize_private_key, serialize_public_key


def main():
    print("Generating RSA-2048 keypair for SENTINEL...")
    private_key = generate_private_key()
    
    private_pem = serialize_private_key(private_key)
    public_pem = serialize_public_key(private_key.public_key())
    
    # Encode as base64
    private_b64 = base64.b64encode(private_pem).decode('utf-8')
    public_b64 = base64.b64encode(public_pem).decode('utf-8')
    
    print("\n" + "="*80)
    print("VERCEL ENVIRONMENT VARIABLES")
    print("="*80)
    print("\nAdd these to your Vercel project settings:\n")
    
    print("SENTINEL_PRIVATE_KEY_CONTENT:")
    print(private_b64)
    print("\nSENTINEL_PUBLIC_KEY_CONTENT:")
    print(public_b64)
    
    print("\n" + "="*80)
    print("IMPORTANT: Keep the private key secret and secure!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
