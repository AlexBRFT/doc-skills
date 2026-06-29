# tr-data-models

Claude plugin for accurate TR-181 data model lookups. Parses Broadband Forum HTML specs into structured JSON so Claude uses exact parameter paths, types, and enums instead of guessing.

## Current Version

**TR-181 Issue 2, Amendment 21 (2-21-0)**

| | USP | CWMP |
|---|---|---|
| Objects | 904 | 948 |
| Parameters | 7,231 | 7,817 |
| Commands | 207 | — |
| Events | 58 | — |

## Installation

**Cowork:** Install as part of the `doc-skills` plugin (this repo).

**Claude.ai:** Go to Settings > Skills, upload the packaged `.skill` file.

## Updating to a New Data Model Version

```bash
# 1. Download new HTML files into raw/
cp tr-181-2-22-0-usp.htm raw/
cp tr-181-2-22-0-cwmp.htm raw/

# 2. Rebuild
pip install beautifulsoup4 lxml  # first time only
./rebuild.sh 2-22-0

# 3. Commit and push
git add -A && git commit -m "TR-181 2-22-0" && git push

# 4. Update plugin in Cowork
```

## Structure

```
tr-data-models/
├── .claude-plugin/
│   └── plugin.json                 # Plugin manifest
├── skills/
│   └── tr-data-models/
│       ├── SKILL.md                # Skill instructions (Claude reads this)
│       ├── scripts/
│       │   └── lookup.py           # Runtime query tool
│       ├── tr181_usp.json          # Parsed USP model (generated)
│       └── tr181_cwmp.json         # Parsed CWMP model (generated)
├── build/
│   └── parse_datamodel.py          # HTML→JSON parser
├── raw/                            # Source HTML from Broadband Forum
├── rebuild.sh                      # One-command rebuild
└── README.md
```
