"""Best-effort metadata stripping for files before encryption.

The production design should strip metadata before client-side encryption. This
module is kept reusable for trusted local preprocessing or server-side demos.
"""

from __future__ import annotations

import io
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def strip_metadata(filename: str, data: bytes) -> bytes:
    """Return file bytes with common metadata removed when supported."""

    suffix = Path(filename).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return strip_image_metadata(data, suffix)
    return data


def strip_image_metadata(data: bytes, suffix: str) -> bytes:
    """Re-encode an image with Pillow, dropping EXIF/XMP metadata."""

    try:
        from PIL import Image
    except ImportError:
        return data

    with Image.open(io.BytesIO(data)) as image:
        clean = Image.new(image.mode, image.size)
        clean.putdata(list(image.getdata()))
        output = io.BytesIO()
        fmt = "JPEG" if suffix in {".jpg", ".jpeg"} else image.format or "PNG"
        save_kwargs = {"format": fmt}
        if fmt == "JPEG":
            save_kwargs["quality"] = 95
        clean.save(output, **save_kwargs)
        return output.getvalue()

