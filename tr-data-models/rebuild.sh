#!/bin/bash
# Rebuild TR-181 data model skill from raw HTML files.
#
# Usage:
#   ./rebuild.sh [VERSION]
#
# Example:
#   ./rebuild.sh 2-21-0
#
# Prerequisites:
#   pip install beautifulsoup4 lxml
#
# Steps:
#   1. Drop new HTML files into raw/ (naming: tr-181-VERSION-usp*.htm, tr-181-VERSION-cwmp*.htm)
#   2. Run: ./rebuild.sh VERSION
#   3. Commit the updated JSON files
#   4. Upload tr-data-models.skill to Claude Settings > Skills

set -euo pipefail
cd "$(dirname "$0")"

VERSION="${1:-2-21-0}"

# Find source files
USP_FILE=$(ls raw/tr-181-${VERSION}*usp*.htm* 2>/dev/null | head -1)
CWMP_FILE=$(ls raw/tr-181-${VERSION}*cwmp*.htm* 2>/dev/null | head -1)

if [ -z "$USP_FILE" ] || [ -z "$CWMP_FILE" ]; then
    echo "ERROR: Could not find HTML files for version $VERSION in raw/"
    echo "Expected pattern: raw/tr-181-${VERSION}*usp*.htm and raw/tr-181-${VERSION}*cwmp*.htm"
    echo ""
    echo "Available files in raw/:"
    ls raw/ 2>/dev/null || echo "  (empty)"
    exit 1
fi

echo "=== Parsing TR-181 $VERSION ==="
echo "  USP:  $USP_FILE"
echo "  CWMP: $CWMP_FILE"
echo ""

python3 scripts/parse_datamodel.py "$USP_FILE" "$CWMP_FILE" . --version "$VERSION"

# Update version in SKILL.md
if command -v sed &>/dev/null; then
    sed -i.bak "s/tr-181-[0-9]-[0-9]*-[0-9]*/tr-181-${VERSION}/g" SKILL.md
    rm -f SKILL.md.bak
    echo ""
    echo "Updated SKILL.md version references to $VERSION"
fi

# Package as .skill (ZIP format)
echo ""
echo "=== Packaging .skill file ==="
SKILL_FILE="tr-data-models.skill"
rm -f "$SKILL_FILE"

# Create temp dir with correct structure
TMPDIR=$(mktemp -d)
SKILL_DIR="$TMPDIR/tr-data-models"
mkdir -p "$SKILL_DIR/scripts"

cp SKILL.md "$SKILL_DIR/"
cp tr181_usp.json "$SKILL_DIR/"
cp tr181_cwmp.json "$SKILL_DIR/"
cp scripts/lookup.py "$SKILL_DIR/scripts/"

(cd "$TMPDIR" && zip -r - tr-data-models/) > "$SKILL_FILE"
rm -rf "$TMPDIR"

echo "Created $SKILL_FILE ($(du -h "$SKILL_FILE" | cut -f1))"
echo ""
echo "=== Done ==="
echo "Next steps:"
echo "  1. git add tr181_usp.json tr181_cwmp.json SKILL.md $SKILL_FILE"
echo "  2. git commit -m 'Update TR-181 data model to $VERSION'"
echo "  3. git push"
echo "  4. Upload $SKILL_FILE to Claude Settings > Skills"
