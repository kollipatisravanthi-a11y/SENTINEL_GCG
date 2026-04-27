# Vercel Deployment Guide for SENTINEL

This guide explains how to deploy SENTINEL on Vercel.

## Prerequisites

1. A Vercel account (https://vercel.com)
2. Your GitHub repository connected to Vercel
3. Python installed locally for generating RSA keys

## Step 1: Generate RSA Keys

Before deploying to Vercel, you need to generate RSA keys and encode them as base64 environment variables.

```bash
python generate_keys.py
```

This will output two base64-encoded strings:
- `SENTINEL_PRIVATE_KEY_CONTENT`
- `SENTINEL_PUBLIC_KEY_CONTENT`

**Keep the private key secret!**

## Step 2: Set Environment Variables on Vercel

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add the following environment variables:

### Required Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `SENTINEL_PRIVATE_KEY_CONTENT` | base64-encoded private key | Generated from `python generate_keys.py` |
| `SENTINEL_PUBLIC_KEY_CONTENT` | base64-encoded public key | Generated from `python generate_keys.py` |
| `SENTINEL_ADMIN_TOKEN` | your-admin-token | Random long string for admin access |
| `SENTINEL_HMAC_SECRET` | your-hmac-secret | Random long string for HMAC operations |

### Optional Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `SENTINEL_NODE_ID` | storage_primary | Node identifier |
| `SENTINEL_ENTRY_NODE` | entry_gateway | Entry node name |
| `SENTINEL_STORAGE_NODE` | storage_node | Storage node name |
| `SENTINEL_MAX_UPLOAD_BYTES` | 10485760 | Max upload size in bytes |
| `SENTINEL_RATE_LIMIT` | 10 per hour | Rate limiting rule |

## Step 3: Deploy

1. Push your changes to GitHub:
   ```bash
   git add .
   git commit -m "Add Vercel deployment configuration"
   git push
   ```

2. Vercel will automatically deploy your project when you push to the main branch.

3. Your application will be available at `https://your-project-name.vercel.app`

## Step 4: Test the Deployment

- **Main page**: `https://your-project-name.vercel.app/`
- **Verify page**: `https://your-project-name.vercel.app/verify`
- **Admin page**: `https://your-project-name.vercel.app/admin`
- **Public key endpoint**: `https://your-project-name.vercel.app/api/v1/public-key`

## Troubleshooting

### "Could not load public key" error

This means the environment variables are not set correctly. Make sure:
1. Both `SENTINEL_PRIVATE_KEY_CONTENT` and `SENTINEL_PUBLIC_KEY_CONTENT` are set
2. They are properly base64-encoded
3. They were generated using `python generate_keys.py`
4. You've redeployed after adding the environment variables

### Database persistence

Note: Vercel uses ephemeral storage. The SQLite database is recreated with each deployment. For production use, consider connecting to an external database service.

## Local Development

To run locally with your generated keys:

1. Create a `.env.local` file:
   ```bash
   cp .env.example .env.local
   ```

2. Update the values with your generated keys (decoded from base64 or use the PEM files)

3. Run the development server:
   ```bash
   pip install -r requirements.txt
   python -m flask --app api.app run
   ```

## Production Considerations

For production deployment:

1. **Use strong secrets**: Generate new `SENTINEL_ADMIN_TOKEN` and `SENTINEL_HMAC_SECRET` values
2. **Database**: Consider using PostgreSQL or MySQL instead of SQLite
3. **Monitoring**: Set up error tracking with Sentry or similar service
4. **Rate limiting**: Adjust `SENTINEL_RATE_LIMIT` based on your needs
5. **Security headers**: Consider adding security headers in `vercel.json`

## Support

For more information about SENTINEL, see the [README.md](README.md) and documentation in the `docs/` directory.
