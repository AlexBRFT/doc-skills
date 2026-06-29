# tr-data-models

Claude skill for accurate TR-181 data model lookups. Parses Broadband Forum HTML data model specs into structured JSON so Claude uses exact parameter paths, types, and enums instead of guessing.

## Current Version

**TR-181 Issue 2, Amendment 21 (2-21-0)**

| | USP | CWMP |
|---|---|---|
| Objects | 904 | 948 |
| Parameters | 7,231 | 7,817 |
| Commands | 207 | — |
| Events | 58 | — |

## Installation

1. Download `tr-data-models.skill` from [Releases](../../releases) or build it yourself
2. Go to Claude Settings → Profile → Skills
3. Upload the `.skill` file

Works in **Claude.ai** and **Cowork** (any environment with compute/bash access).

## Updating to a New Data Model Version

```bash
# 1. Download new HTML files from Broadband Forum
#    USP: https://usp-data-models.broadband-forum.org/tr-181-VERSION-usp.html
#    CWMP: https://cwmp-data-models.broadband-forum.org/tr-181-VERSION-cwmp.html

# 2. Save them in raw/
cp tr-181-2-22-0-usp.htm raw/
cp tr-181-2-22-0-cwmp.htm raw/

# 3. Rebuild
pip install beautifulsoup4 lxml  # first time only
./rebuild.sh 2-22-0

# 4. Commit and push
git add -A
git commit -m "Update TR-181 to 2-22-0"
git push

# 5. Upload tr-data-models.skill to Claude Settings > Skills
```

## Repo Structure

```
tr-data-models/
├── SKILL.md                    # Skill instructions (loaded by Claude)
├── rebuild.sh                  # One-command rebuild + package
├── tr181_usp.json              # Parsed USP data model (generated)
├── tr181_cwmp.json             # Parsed CWMP data model (generated)
├── tr-data-models.skill        # Packaged skill file (generated)
├── scripts/
│   ├── lookup.py               # Runtime query tool (used by Claude)
│   └── parse_datamodel.py      # HTML→JSON parser (used by rebuild.sh)
├── raw/                        # Source HTML files from Broadband Forum
│   ├── tr-181-2-21-0-usp_xml.htm
│   └── tr-181-2-21-0-cwmp_xml.htm
└── README.md
```

## How It Works

When you mention TR-181 paths, USP/CWMP parameters, or Device.* objects in a conversation, Claude reads the SKILL.md and runs `lookup.py` to query the parsed JSON. No guessing, no hallucinated parameters.

### Lookup Commands (used by Claude internally)

```bash
# Get exact parameter details
python3 scripts/lookup.py usp get Device.WiFi.Radio.Channel

# List children of an object
python3 scripts/lookup.py cwmp children Device.ManagementServer.

# Search by substring
python3 scripts/lookup.py usp search SSID

# Show object tree
python3 scripts/lookup.py usp tree Device.WiFi.

# List commands/events
python3 scripts/lookup.py usp commands Device.WiFi.
python3 scripts/lookup.py usp events Device.

# Compare USP vs CWMP
python3 scripts/lookup.py usp diff
```

## Requirements

- Python 3.8+
- `beautifulsoup4` and `lxml` (for parsing only, not needed at runtime)
