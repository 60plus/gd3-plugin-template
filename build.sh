#!/bin/bash
# Build a plugin ZIP for distribution.
# Usage: ./build.sh <plugin-directory>
# Example: ./build.sh examples/ppe-metadata

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <plugin-directory>"
  echo "Example: $0 examples/ppe-metadata"
  exit 1
fi

DIR="$1"
if [ ! -f "$DIR/plugin.json" ]; then
  echo "Error: $DIR/plugin.json not found"
  exit 1
fi

# Read plugin ID and version from manifest
ID=$(python3 -c "import json; print(json.load(open('$DIR/plugin.json'))['id'])")
VER=$(python3 -c "import json; print(json.load(open('$DIR/plugin.json'))['version'])")
BASENAME=$(basename "$DIR")
OUTFILE="${ID}-v${VER}.zip"

echo "Building $OUTFILE from $DIR ..."

# Create ZIP with the plugin directory as root
cd "$(dirname "$DIR")"
zip -r "../$OUTFILE" "$BASENAME/" -x "*__pycache__*" "*.pyc"
cd ..

echo "Created: $OUTFILE"
echo "Install via Settings > Plugins in GamesDownloader."
