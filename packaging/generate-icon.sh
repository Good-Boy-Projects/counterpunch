#!/usr/bin/env bash
# generate-icon.sh — build a macOS .icns from a single source PNG.
#
# Usage: ./generate-icon.sh path/to/source-1024.png
#
# Requirements for the source image:
#   - 1024x1024 pixels (square)
#   - PNG, ideally with transparency
#   - No baked-in rounded corners or drop shadow — macOS applies its own
#     "squircle" mask and shadow automatically.
set -euo pipefail

SOURCE="$1"
ICONSET_DIR="TruFont.iconset"
OUTPUT="TruFont.icns"

if [ ! -f "$SOURCE" ]; then
  echo "Source file not found: $SOURCE"
  exit 1
fi

rm -rf "$ICONSET_DIR"
mkdir "$ICONSET_DIR"

sips -z 16 16     "$SOURCE" --out "$ICONSET_DIR/icon_16x16.png"
sips -z 32 32     "$SOURCE" --out "$ICONSET_DIR/icon_16x16@2x.png"
sips -z 32 32     "$SOURCE" --out "$ICONSET_DIR/icon_32x32.png"
sips -z 64 64     "$SOURCE" --out "$ICONSET_DIR/icon_32x32@2x.png"
sips -z 128 128   "$SOURCE" --out "$ICONSET_DIR/icon_128x128.png"
sips -z 256 256   "$SOURCE" --out "$ICONSET_DIR/icon_128x128@2x.png"
sips -z 256 256   "$SOURCE" --out "$ICONSET_DIR/icon_256x256.png"
sips -z 512 512   "$SOURCE" --out "$ICONSET_DIR/icon_256x256@2x.png"
sips -z 512 512   "$SOURCE" --out "$ICONSET_DIR/icon_512x512.png"
cp "$SOURCE"                "$ICONSET_DIR/icon_512x512@2x.png"

iconutil -c icns "$ICONSET_DIR" -o "$OUTPUT"
rm -rf "$ICONSET_DIR"

echo "Built $OUTPUT"
