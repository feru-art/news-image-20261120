#!/usr/bin/env python3
"""Friday 20 November 2026 — the world's news in one image.

Entry for make.fun news-image-20261120 (pot $250, top 50).

The picture this program ships was made with Generate Image (Milku):
a dense front-page tile. Cyclone Akvan's landfall near Gopalpur, India
is the hero; five photo tiles cover the APEC trilateral in Shenzhen,
the ICJ's Rohingya genocide verdict, the Kyiv embassy strikes, GTA VI's
second day in Vice City, and South Korea clearing ex-PM Han.

This program draws nothing. It carries the finished picture as
``image.jpg`` beside this file and copies those exact bytes to the
grader's output path, so every run writes identical bytes. The file is
a JPEG (named ``entry.png`` either way, as the rules allow), 1024x1024
and under 1 MiB.
"""

import hashlib
import os
import struct
import sys
from pathlib import Path

SOURCE_NAME = "image.jpg"
OUTPUT_NAME = "entry.png"
MAX_BYTES = 1_048_576
MAX_SIDE = 1024
EXPECTED_SIZE = (1024, 1024)


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    """Read width/height from the first SOF marker of a JPEG stream.

    Walks the marker segments after SOI; SOF0/SOF1/SOF2 carry the frame
    height and width as big-endian 16-bit values. Raises ValueError when
    no frame header is found, so a truncated file cannot slip through.
    """
    pos = 2  # skip SOI
    while pos + 9 <= len(data):
        if data[pos] != 0xFF:
            raise ValueError(f"bad marker prefix at offset {pos}")
        marker = data[pos + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        seg_len = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2):  # SOF0, SOF1, SOF2
            height, width = struct.unpack(">HH", data[pos + 5:pos + 9])
            return width, height
        pos += 2 + seg_len
    raise ValueError("no SOF frame header found in JPEG")


def resolve_output_dir() -> Path:
    """Pick the writable output directory, in priority order."""
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if env_dir:
        return Path(env_dir)
    default = Path("/output")
    if default.is_dir():
        return default
    return Path.cwd() / "output"


def load_source() -> bytes:
    source = Path(__file__).resolve().parent / SOURCE_NAME
    data = source.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit(f"image too large: {len(data)} bytes > {MAX_BYTES}")
    if not data.startswith(b"\xff\xd8\xff") or not data.rstrip(b"\x00").endswith(b"\xff\xd9"):
        raise SystemExit("image is not a complete JPEG (bad SOI/EOI markers)")
    width, height = jpeg_dimensions(data)
    if (width, height) != EXPECTED_SIZE:
        raise SystemExit(f"image is {width}x{height}, expected 1024x1024")
    return data


def main() -> int:
    if "--check" in sys.argv[1:]:
        data = load_source()
        print(f"ok: {len(data)} bytes, 1024x1024 JPEG, "
              f"sha256 {hashlib.sha256(data).hexdigest()}")
        return 0
    data = load_source()
    out_dir = resolve_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / OUTPUT_NAME
    out_path.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    print(f"wrote {out_path} ({len(data)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
