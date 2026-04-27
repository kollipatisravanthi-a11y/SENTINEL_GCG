# Recent Updates

## Version 1.1 - Enhanced Admin Dashboard

### New Features

#### 1. **Attachment Download & Preview**
Admins can now interact with encrypted attachments in the dashboard:

**Download Button**
- Download encrypted attachments directly to your device
- Maintains file integrity with SHA-256 verification
- Preserves original filename and file type

**Preview Button**
Supports multiple file types:
- **Images** (PNG, JPG, GIF, WebP, etc.) - Displayed inline
- **PDFs** - Embedded viewer
- **Text files** (TXT, MD, CSV, etc.) - Formatted display
- **Other files** - Download prompt with helpful message

### Technical Implementation

**Frontend Changes** (`client/web/admin.html`)
- Added action buttons: Download and Preview
- Implemented file type detection (MIME type)
- Base64 decoding for binary data
- Object URL handling for secure preview

**API Enhancement** (`server/app.py`)
- `/api/v1/admin/decrypt` now supports `include_attachment_data` parameter
- Full attachment data returned with Base64-encoded binary content
- SHA-256 hash provided for integrity verification

### Security Notes

- Attachments remain encrypted in database
- Only decrypted in memory when admin requests
- File preview occurs client-side (browser)
- No file data stored in browser cache
- Integrity verified via cryptographic hash

### Files Modified

- `client/web/admin.html` - Added preview UI and download/preview functions
- `server/app.py` - Enhanced decrypt endpoint (no breaking changes)

### Backward Compatibility

✓ Fully backward compatible - existing reports work without changes

### Demo Workflow

1. Submit a complaint with an image/PDF attachment
2. Go to `/admin` with token: `sentinel-admin-dev-token`
3. Load reports
4. Click a complaint with attachment
5. Click **Preview** to see the file inline
6. Click **Download** to save the file locally

---

## Next Steps

- Deploy to Google Cloud Run for public access
- Add Tor hidden service support
- Integrate with Secret Manager for key storage
- Production database hardening

