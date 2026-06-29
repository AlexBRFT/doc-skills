#!/bin/bash
# Rebuild TR-181 data model from raw HTML files.
# Usage: ./rebuild.sh [VERSION]
# Example: ./rebuild.sh 2-22-0
# Prerequisites: pip install beautifulsoup4 lxml

set -euo pipefail
cd "$(dirname "$0")"

VERSION="${1:-2-21-0}"
SKILL_DIR="skills/tr-data-models"

USP_FILE=$(ls raw/tr-181-${VERSION}*usp*.htm* 2>/dev/null | head -1)
CWMP_FILE=$(ls raw/tr-181-${VERSION}*cwmp*.htm* 2>/dev/null | head -1)

if [ -z "$USP_FILE" ] || [ -z "$CWMP_FILE" ]; then
    echo "ERROR: HTML files for version $VERSION not found in raw/"
    echo "Expected: raw/tr-181-${VERSION}*usp*.htm and raw/tr-181-${VERSION}*cwmp*.htm"
    ls raw/ 2>/dev/null || echo "  (empty)"
    exit 1
fi

echo "=== Parsing TR-181 $VERSION ==="
python3 build/parse_datamodel.py "$USP_FILE" "$CWMP_FILE" "$SKILL_DIR" --version "$VERSION"

# Update version in SKILL.md
sed -i.bak "s/tr-181-[0-9]-[0-9]*-[0-9]*/tr-181-${VERSION}/g" "$SKILL_DIR/SKILL.md"
rm -f "$SKILL_DIR/SKILL.md.bak"

echo ""
echo "=== Done ==="
echo "Commit and push, then update the plugin in Cowork."
echo "Or package as .skill: zip -r tr-data-models.skill $SKILL_DIR/"
