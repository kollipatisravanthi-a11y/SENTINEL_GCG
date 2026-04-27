# SENTINEL Architecture

## Identity

SENTINEL is an anonymous tamper-evident whistleblower network.

Tagline: Submit once. Prove forever. Stay anonymous always.

Core promise: a user can submit a report, receive a cryptographic receipt, and
later prove that the encrypted report has not been modified.

## Course Mapping

Computer Networks:

- HTTP API design with browser-to-server submission.
- Tor-compatible hidden-service deployment model.
- No account, cookie, session, analytics, or IP-retention workflow.
- Simulated relay network with weighted paths and failover-friendly topology.

Algorithms:

- Dijkstra shortest path for relay selection.
- Merkle tree construction and O(log n) proof verification.
- SHA-256 hashing and HMAC-SHA256 receipts.
- Hybrid encryption using AES-256-GCM and RSA-2048 OAEP.

## Web Submission Flow

1. Browser fetches the server RSA public key from `/api/v1/public-key`.
2. Browser creates a JSON payload from the form fields.
3. Browser generates a fresh AES-256 key and 96-bit GCM IV.
4. Browser encrypts the payload with AES-256-GCM.
5. Browser wraps the AES key with RSA-OAEP SHA-256.
6. Browser submits only encrypted fields to `/api/v1/submit`.
7. Server assembles a canonical encrypted blob.
8. Server computes `report_id = HMAC-SHA256(blob, server_secret)`.
9. Server stores the blob in SQLite and returns the receipt.

No plaintext report body is stored by the server.

## Server Layers

API:

- `server/app.py` exposes submit, verify, public-key, Merkle-root, and admin
  list/decrypt endpoints.
- Rate limiting is enabled when `flask-limiter` is installed.
- The app never stores submitter identity fields.

Crypto:

- `crypto/aes_engine.py` handles AES-256-GCM encryption and decryption.
- `crypto/rsa_engine.py` handles RSA key generation and AES-key wrapping.
- `crypto/hmac_engine.py` creates and verifies 64-character receipts.
- `crypto/envelope.py` defines the exact byte format sealed by HMAC.

Routing:

- `routing/graph.py` models relay nodes as a weighted directed graph.
- `routing/dijkstra.py` selects the minimum-latency path.
- The selected path is stored for demo visibility.

Storage:

- SQLite stores `report_id`, encrypted blob, Merkle index, submitted order,
  storage node, and simulated relay path.
- `storage/merkle.py` builds roots and proof paths from encrypted blob hashes.

Audit:

- `audit/verifier.py` recomputes the HMAC and builds a Merkle proof.
- A report is `VALID` only when the stored blob still matches the receipt and
  the proof path reconstructs the current Merkle root.

Admin review:

- `/admin` gives authorized organization reviewers a private dashboard.
- Reviewers enter the admin token, load submitted complaints, open a complaint,
  decrypt it, and see the current integrity status.
- The dashboard never displays submitter identity because the system never
  collects it.

Anonymity:

- The design is compatible with Tor hidden-service deployment.
- The browser uses no cookies or local storage.
- Metadata stripping helpers are available for trusted preprocessing. Because
  the report is encrypted before upload, file metadata should be removed before
  encryption when a real deployment requires strict metadata hygiene.

## Data Model

```sql
CREATE TABLE reports (
    report_id TEXT PRIMARY KEY,
    encrypted_blob BLOB NOT NULL,
    merkle_index INTEGER NOT NULL,
    submitted_at INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    route_path TEXT NOT NULL DEFAULT ''
);
```

## Demo Script

1. Start the API: `python server/app.py`.
2. Open `http://127.0.0.1:5000/`.
3. Submit a report and copy the receipt.
4. Open `http://127.0.0.1:5000/admin`.
5. Enter the admin token and open the complaint.
6. Open `http://127.0.0.1:5000/verify`.
7. Paste the receipt and verify `VALID`.
8. Modify one byte of `encrypted_blob` in SQLite.
9. Verify the receipt again and observe `TAMPERED`.
