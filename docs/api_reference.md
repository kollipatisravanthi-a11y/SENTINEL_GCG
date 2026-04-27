# SENTINEL API Reference

Base URL for local demo: `http://127.0.0.1:5000`

## `GET /api/v1/public-key`

Returns the RSA public key used by the browser to wrap the AES key.

Response:

```json
{
  "public_key_pem": "-----BEGIN PUBLIC KEY-----..."
}
```

## `POST /api/v1/submit`

Stores an encrypted report blob and returns the receipt.

Request:

```json
{
  "ciphertext": "base64",
  "auth_tag": "base64",
  "iv": "base64",
  "encrypted_key": "base64"
}
```

Response:

```json
{
  "report_id": "64 hex characters",
  "status": "STORED",
  "duplicate": false,
  "merkle_index": 0,
  "merkle_root": "64 hex characters",
  "node_id": "storage_primary",
  "route": {
    "cost_ms": 51,
    "path": ["entry_gateway", "relay_2", "relay_4", "storage_node"]
  }
}
```

## `GET /api/v1/verify/<report_id>`

Verifies that a stored blob still matches its HMAC receipt and Merkle proof.

Responses:

```json
{
  "status": "VALID",
  "report_id": "64 hex characters",
  "leaf_hash": "64 hex characters",
  "merkle_root": "64 hex characters",
  "merkle_proof": [
    { "position": "right", "hash": "64 hex characters" }
  ],
  "proof_valid": true,
  "merkle_index": 0,
  "node_id": "storage_primary",
  "route_path": "entry_gateway -> relay_2 -> relay_4 -> storage_node"
}
```

`status` can be `VALID`, `TAMPERED`, `NOT_FOUND`, or `INVALID_RECEIPT`.

## `GET /api/v1/audit/merkle-root`

Returns the current public audit root.

```json
{
  "merkle_root": "64 hex characters",
  "report_count": 1
}
```

## `GET /api/v1/admin/reports`

Lists encrypted report records for authorized organization reviewers.

Headers:

```text
X-Admin-Token: sentinel-admin-dev-token
```

Response:

```json
{
  "report_count": 1,
  "merkle_root": "64 hex characters",
  "reports": [
    {
      "report_id": "64 hex characters",
      "status": "VALID",
      "merkle_index": 0,
      "submitted_at": 1710000000,
      "node_id": "storage_primary",
      "route_path": "entry_gateway -> relay_2 -> relay_4 -> storage_node",
      "leaf_hash": "64 hex characters"
    }
  ]
}
```

## `POST /api/v1/admin/decrypt`

Decrypts a report for authorized demo administration.

Headers:

```text
X-Admin-Token: sentinel-admin-dev-token
```

Request:

```json
{
  "report_id": "64 hex characters",
  "include_attachment_data": false
}
```

Response:

```json
{
  "report_id": "64 hex characters",
  "integrity": {
    "status": "VALID",
    "leaf_hash": "64 hex characters",
    "merkle_root": "64 hex characters",
    "proof_valid": true,
    "merkle_index": 0
  },
  "payload": {
    "title": "optional title",
    "body": "report text",
    "attachment": null,
    "client": "web-interface"
  }
}
```
