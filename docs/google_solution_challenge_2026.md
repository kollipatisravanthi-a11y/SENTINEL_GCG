# Google Solution Challenge 2026 Positioning

## Team

Team name: **BitMaster**

Project name: **SENTINEL**

Tagline: Submit once. Prove forever. Stay anonymous always.

## Selected UN SDG

**SDG 16: Peace, Justice and Strong Institutions**

SENTINEL supports safer reporting channels for misconduct, corruption, abuse,
fraud, and institutional wrongdoing. The project is designed around trust,
accountability, and evidence integrity.

## Target Users

- Whistleblowers and citizens submitting sensitive complaints
- Journalists and public-interest investigators verifying reports
- Legal aid groups checking evidence integrity
- Internal ethics or compliance teams reviewing complaints
- Student bodies or university cells receiving anonymous grievances

## Core Problem

Complaint systems often fail because submitters do not trust them. A submitter
may fear identity exposure, and reviewers may later face claims that evidence
was modified or fabricated. SENTINEL provides a demo-ready proof that encrypted
reports can be stored and later verified for integrity.

## Solution Summary

SENTINEL provides three flows:

1. Anonymous complaint submission from a browser.
2. Organization review through an admin dashboard.
3. Public receipt verification for tamper detection.

The system stores encrypted complaints, issues a cryptographic receipt, and
uses Merkle proofs to prove whether a stored complaint has changed.

## Google Technology Alignment

Implemented:

- Dockerized Flask app suitable for Google Cloud Run.
- Cloud Build pipeline file for automated build and deploy.

Planned production Google Cloud services:

- Cloud Run for scalable hosting.
- Secret Manager for secrets and private key material.
- Cloud SQL for production-grade relational storage.
- Cloud Storage for encrypted evidence attachments.
- Cloud Monitoring for service health.

## Evaluation Story

Impact:

- Gives vulnerable users a safer reporting channel.
- Helps organizations demonstrate complaint integrity.
- Makes evidence tampering visible instead of silent.

Technology:

- Browser-side encryption.
- HMAC receipts.
- Merkle proof verification.
- Dijkstra route simulation.
- Google Cloud Run deployment path.

User experience:

- Submit page is simple and login-free.
- Receipt verification is one field.
- Admin dashboard gives reviewers a clear complaint list and detail view.

Feasibility:

- Runs locally with Python.
- Has automated tests.
- Can be containerized and deployed to Cloud Run.
- Uses environment variables for deploy-time configuration.

## Roadmap

Prototype:

- Local Flask app
- SQLite storage
- Demo admin token
- Local generated RSA keys

Next version:

- Google Cloud Run deployment
- Secret Manager integration
- Cloud SQL database
- Strong admin login
- Public Merkle-root history

Production vision:

- Tor hidden service
- Independent audit logs
- Legal/evidence export workflow
- Multi-organization deployment model
- External root anchoring for stronger public accountability

## References

- Google Solution Challenge: https://developers.google.com/community/gdsc-solution-challenge
- Google Solution Challenge terms: https://developers.google.com/community/gdsc-solution-challenge/terms
- UN SDG 16: https://sdgs.un.org/goals/goal16
