#!/usr/bin/env bash
# build-app.sh — build a versioned Counterpunch.app for local testing.
#
# Usage:
#   ./build-app.sh                    # uses current git describe as version
#   ./build-app.sh phase-3-complete   # uses an explicit version/tag label
#
# Output lands in dist/Counterpunch.app, and a copy is archived in
# builds/Counterpunch-<version>.app so you keep a history of testable builds
# across phases without overwriting the previous one.
set -euo pipefail

VERSION="${1:-$(git describe --tags --always --dirty)}"
echo "Building Counterpunch.app — version label: $VERSION"

export TRUFONT_BUILD_VERSION="$VERSION"

# Clean previous build artifacts so stale files don't leak into the new one
rm -rf build dist

pyinstaller packaging/trufont.spec

mkdir -p builds
cp -R "dist/Counterpunch.app" "builds/Counterpunch-$VERSION.app"

echo ""
echo "Done."
echo "  Latest build:   dist/Counterpunch.app"
echo "  Archived copy:  builds/Counterpunch-$VERSION.app"
echo ""
echo "First launch will need a right-click > Open (unsigned build, Gatekeeper"
echo "will otherwise refuse to run it via double-click the first time)."
