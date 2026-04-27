# Google Cloud Deployment Guide

This project is prepared for Google Cloud Run deployment through `Dockerfile`
and `cloudbuild.yaml`.

## Local Container Build

```bash
docker build -t sentinel-bitmaster .
docker run -p 8080:8080 \
  -e SENTINEL_ADMIN_TOKEN=change-me \
  -e SENTINEL_HMAC_SECRET=change-me-too \
  sentinel-bitmaster
```

Open:

```text
http://127.0.0.1:8080/
```

## Cloud Run Deployment Outline

1. Create a Google Cloud project.
2. Enable Cloud Run, Cloud Build, and Artifact Registry.
3. Create an Artifact Registry Docker repository named `sentinel`.
4. Configure secrets for:
   - `SENTINEL_ADMIN_TOKEN`
   - `SENTINEL_HMAC_SECRET`
5. Deploy with Cloud Build.

Example:

```bash
gcloud builds submit --config cloudbuild.yaml
```

## Production Notes

The local prototype stores SQLite data on local disk. Cloud Run file storage is
ephemeral, so production deployment should move persistent storage to Cloud SQL
or another durable Google Cloud database.

