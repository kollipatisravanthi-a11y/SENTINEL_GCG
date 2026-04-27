# SENTINEL

**Anonymous Tamper-Evident Whistleblower Network**

Google Solution Challenge 2026 submission by **Team BitMaster**.

SENTINEL helps people submit sensitive complaints safely, gives them a receipt,
and lets anyone verify later whether the stored complaint has been changed.

## Challenge Focus

SENTINEL is aligned with **UN Sustainable Development Goal 16: Peace, Justice
and Strong Institutions**. The project focuses on safer reporting, accountable
institutions, and tamper-evident handling of complaints.

Google Solution Challenge projects are expected to solve one or more UN
Sustainable Development Goals using Google technology. SENTINEL is prepared for
deployment on **Google Cloud Run**, with a path toward Secret Manager and Cloud
SQL for production hardening.

## Problem

People often avoid reporting corruption, abuse, fraud, unsafe practices, or
institutional wrongdoing because they fear two things:

- Their identity may be exposed.
- Their complaint may be edited, deleted, or denied later.

SENTINEL addresses both risks in a demo-ready way:

- No login is required for submitting a report.
- The browser encrypts the complaint before upload.
- The system returns a receipt.
- Verification detects whether stored evidence was changed.
- Authorized organization reviewers can read complaints from an admin dashboard.

## What It Does

1. A whistleblower opens the submission page.
2. They write a complaint and optionally attach evidence.
3. The browser encrypts the complaint before sending it to the server.
4. The server stores only the encrypted report.
5. The user receives a 64-character receipt ID.
6. The organization opens the admin dashboard and reviews complaints.
7. Anyone with the receipt can verify whether the stored complaint is still
   intact.
8. If the database record is changed manually, SENTINEL marks it as
   `TAMPERED`.

## Live Pages

When running locally:

- Submit complaint: `http://127.0.0.1:5000/`
- Verify receipt: `http://127.0.0.1:5000/verify`
- Organization dashboard: `http://127.0.0.1:5000/admin`

Default demo admin token:

```text
sentinel-admin-dev-token
```

This token is only for demo use. Use a strong environment variable in real
deployment.

## Why It Is Tamper-Evident

SENTINEL gives each report a receipt based on the exact encrypted bytes stored
in the database. It also places stored reports into a Merkle tree.

In simple terms:

- **Receipt ID** proves one specific complaint was stored.
- **Leaf hash** is the fingerprint of one complaint.
- **Merkle root** is the fingerprint of all stored complaints together.
- **Merkle proof** proves one complaint belongs to the current root.
- If stored data changes, verification shows `TAMPERED`.

## Google Technology Use

Current repository:

- **Google Cloud Run-ready Docker deployment**
- **Cloud Build configuration** for build and deploy automation
- Browser Web Crypto API for client-side encryption

Production roadmap:

- Google Cloud Run for hosting
- Google Secret Manager for admin token, HMAC secret, and private key material
- Cloud SQL for production database storage
- Cloud Storage for encrypted large attachments
- Cloud Monitoring for uptime and operational health

## Quick Start

```powershell
cd "C:\Users\Manoj\OneDrive\Documents\SENTINEL"
python -m pip install -r requirements.txt
python server/app.py
```

Open:

```text
http://127.0.0.1:5000/
```

## Environment Variables

Copy `.env.example` and set strong values for real deployment:

```text
SENTINEL_ADMIN_TOKEN=replace-with-a-long-random-admin-token
SENTINEL_HMAC_SECRET=replace-with-a-long-random-hmac-secret
SENTINEL_HOST=127.0.0.1
SENTINEL_PORT=5000
```

For Cloud Run, the app reads the platform-provided `PORT` variable.

## Demo Script

1. Start the server: `python server/app.py`.
2. Open the submit page.
3. Submit a sample complaint.
4. Copy the receipt ID.
5. Open `/admin`.
6. Enter the admin token and load reports.
7. Open the complaint and show its `VALID` status.
8. Open `/verify`.
9. Paste the receipt and verify `VALID`.
10. Manually alter the encrypted database blob.
11. Verify again and show `TAMPERED`.

## Run Tests

```powershell
python -m pytest tests --basetemp .pytest_tmp -p no:cacheprovider
```

Expected result:

```text
10 passed
```

## Project Structure

```text
client/
  web/
    index.html          # complaint submission page
    verify.html         # public receipt verification page
    admin.html          # organization review dashboard
    crypto.js           # browser encryption helpers
server/
  app.py                # Flask API and page routes
  config.py             # environment-backed configuration
  crypto/               # AES, RSA, HMAC, envelope helpers
  routing/              # Dijkstra relay path simulation
  storage/              # SQLite and Merkle tree logic
  audit/                # verification logic
  anonymity/            # metadata stripping helper
tests/                  # pytest coverage
docs/                   # architecture, API, challenge notes
Dockerfile              # Cloud Run-ready container
cloudbuild.yaml         # Cloud Build deployment pipeline
```

## Security Notes

This is a challenge prototype, not a production whistleblower platform.

For real-world use, the system should add:

- Tor hidden service deployment
- Secret Manager-backed key storage
- Proper organization authentication with MFA
- External Merkle-root anchoring
- Strong metadata stripping before encryption
- Production database backups and retention policy
- Independent security review

## Team

**BitMaster**

- Project: SENTINEL
- Theme: Anonymous, tamper-evident complaint reporting
- SDG: 16 - Peace, Justice and Strong Institutions

## References

- Google Solution Challenge: https://developers.google.com/community/gdsc-solution-challenge
- Google Solution Challenge terms: https://developers.google.com/community/gdsc-solution-challenge/terms
- UN SDG 16: https://sdgs.un.org/goals/goal16

