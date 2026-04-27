# Vercel Deployment Guide for SENTINEL

This guide explains how to deploy SENTINEL on Vercel.

## Prerequisites

1. A Vercel account (https://vercel.com)
2. Your GitHub repository connected to Vercel

## Step 1: Environment Variables

Only two environment variables are required on Vercel:

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add the following variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `SENTINEL_ADMIN_TOKEN` | `your-secure-admin-token` | Random long string for admin access |
| `SENTINEL_HMAC_SECRET` | `your-secure-hmac-secret` | Random long string for HMAC operations |

**Note:** RSA keys are automatically generated and stored in the project's `data/` directory.

## Step 2: Deploy

1. Go to https://vercel.com/new
2. Click **Import a Git Repository**
3. Select your SENTINEL repository
4. Enter a **Project Name**: `sentinelgcg` or `SENTINEL_GCG`
5. Click **Environment Variables** and add:
   - `SENTINEL_ADMIN_TOKEN` = your secure token
   - `SENTINEL_HMAC_SECRET` = your secure secret
6. Click **Deploy**

Your application will be available at `https://your-project-name.vercel.app`

## Step 3: Test the Deployment

- **Main page**: `https://your-project-name.vercel.app/`
- **Verify page**: `https://your-project-name.vercel.app/verify`
- **Admin page**: `https://your-project-name.vercel.app/admin`
- **Public key endpoint**: `https://your-project-name.vercel.app/api/v1/public-key`

## How It Works

- **RSA Keys**: Automatically generated on first deployment and stored in `/data/` directory in the project
- **Secrets**: Only `SENTINEL_ADMIN_TOKEN` and `SENTINEL_HMAC_SECRET` need to be in environment variables
- **Database**: Uses SQLite (ephemeral storage - recreated with each deployment)

## Local Development

To run locally:

1. Create a `.env.local` file:
   ```
   SENTINEL_ADMIN_TOKEN=your-admin-token
   SENTINEL_HMAC_SECRET=your-hmac-secret
   ```

2. Run the development server:
   ```bash
   pip install -r requirements.txt
   python -m flask --app api.app run
   ```

The RSA keys will be automatically generated in the `data/` directory on first run.

## Production Considerations

For production deployment:

1. **Use strong secrets**: Generate new, cryptographically secure tokens for `SENTINEL_ADMIN_TOKEN` and `SENTINEL_HMAC_SECRET`
2. **Database**: Consider using PostgreSQL or MySQL instead of SQLite
3. **Rate limiting**: Adjust `SENTINEL_RATE_LIMIT` based on your needs
4. **Monitoring**: Set up error tracking with Sentry or similar service

## Support

For more information about SENTINEL, see the [README.md](README.md) and documentation in the `docs/` directory.
