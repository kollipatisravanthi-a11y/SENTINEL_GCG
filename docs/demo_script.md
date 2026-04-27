# Demo Script

## 2-Minute Pitch

SENTINEL is a tamper-evident anonymous complaint system by Team BitMaster. It
supports SDG 16 by helping people report wrongdoing while preserving evidence
integrity.

The core idea is simple: a person submits a complaint, receives a receipt, and
can later prove whether that complaint was changed. The organization can review
complaints from an admin dashboard, but the system does not collect submitter
identity.

## Live Demo Flow

1. Open the submit page.
2. Type a complaint.
3. Submit it and copy the receipt.
4. Open the admin dashboard.
5. Enter the demo admin token.
6. Load reports.
7. Open the complaint and show its content.
8. Open the verify page.
9. Paste the receipt and show `VALID`.
10. Explain that if anyone changes the database record, verification becomes
    `TAMPERED`.

## Demo Admin Token

```text
sentinel-admin-dev-token
```

## Suggested Explanation

The important part is not that nobody can ever attack a server. The important
part is that silent tampering becomes detectable. If a powerful insider changes
the stored complaint, the receipt and Merkle proof no longer match.

