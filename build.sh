#!/bin/bash
# Build a plugin ZIP for distribution.
# Produces an archive with plugin.json at the ROOT (required by GamesDownloader:
# the installer reads /plugin.json, not /<folder>/plugin.json).
# Usage: ./build.sh <plugin-directory>
# Example: ./build.sh examples/ppe-metadata

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <plugin-directory>"
  echo "Example: $0 examples/ppe-metadata"
  exit 1
fi

DIR="${1%/}"
if [ ! -f "$DIR/plugin.json" ]; then
  echo "Error: $DIR/plugin.json not found"
  exit 1
fi

# Read plugin ID and version from the manifest
ID=$(python3 -c "import json; print(json.load(open('$DIR/plugin.json'))['id'])")
VER=$(python3 -c "import json; print(json.load(open('$DIR/plugin.json'))['version'])")
OUTFILE="${ID}-v${VER}.zip"
OUT_ABS="$(pwd)/$OUTFILE"

echo "Building $OUTFILE from $DIR ..."

# Zip the plugin's CONTENTS at the archive root (so plugin.json is NOT nested
# under a wrapping folder), with forward-slash paths and no Python caches.
rm -f "$OUT_ABS"
( cd "$DIR" && zip -rq "$OUT_ABS" . -x "*__pycache__*" "*.pyc" "*.DS_Store" "*/.git/*" )

echo "Created: $OUTFILE"
echo
echo "Verifying archive layout (plugin.json must appear with no path prefix):"
if unzip -l "$OUT_ABS" | grep -qE " plugin\.json$"; then
  unzip -l "$OUT_ABS" | grep -E " plugin\.json$"
else
  echo "ERROR: plugin.json is not at the ZIP root - install would fail."
  exit 1
fi
echo
echo "Install via Settings > Plugins in GamesDownloader (or publish to a store)."
