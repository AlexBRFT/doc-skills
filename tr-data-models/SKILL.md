---
name: tr-data-models
description: Use this skill whenever the user mentions TR-181, TR-369, USP, CWMP, CPE data model, Device data model, broadband forum data model, or references any Device.* parameter path. Also trigger when writing code, configs, scripts, or documents that reference TR-181 object paths, parameters, commands, or events. This skill provides parsed, authoritative TR-181-2-21-0 data model definitions for both USP and CWMP protocols. NEVER guess parameter paths or types — always look them up using this skill.
---

# TR-181 Data Model Lookup

## Purpose
Provide exact, parse-based access to TR-181 Device:2.21 data model for USP and CWMP protocols. This is the ONLY source of truth for parameter paths, types, access modes, enums, commands, and events.

## Data Model Version
- Model: TR-181 Issue 2, Amendment 21 (tr-181-2-21-0)
- USP: 904 objects, 7231 parameters, 207 commands, 58 events
- CWMP: 948 objects, 7817 parameters (no commands/events)
- Source: https://cwmp-data-models.broadband-forum.org/tr-181-2-21-0-cwmp.html / https://usp-data-models.broadband-forum.org/tr-181-2-21-0-usp.html

## Critical Rules
1. NEVER invent, guess, or recall parameter paths from training data. Always run the lookup script.
2. NEVER assume a parameter exists in both USP and CWMP — they differ.
3. NEVER guess parameter types, access modes, or enum values — look them up.
4. Commands and Events exist ONLY in USP, never in CWMP.
5. Multi-instance objects have type `object(0:)`. Use `{i}` placeholder in actual protocol paths (e.g. `Device.WiFi.Radio.{i}.Channel`), but the lookup tool stores them without `{i}` (e.g. `Device.WiFi.Radio.Channel`).

## How to Look Up

Run via bash: `python3 <SKILL_DIR>/scripts/lookup.py <protocol> <action> <query>`

Where `<SKILL_DIR>` is the directory containing this SKILL.md.

### Actions

| Action | What it does | Example |
|--------|-------------|---------|
| `get <path>` | Full details of exact path | `usp get Device.WiFi.Radio.Channel` |
| `children <path>` | Direct children of an object | `usp children Device.WiFi.` |
| `search <pattern>` | Substring search, case-insensitive | `usp search SSID` |
| `tree <path>` | Object subtree, 3 levels deep | `cwmp tree Device.IP.` |
| `commands [prefix]` | List USP commands | `usp commands Device.WiFi.` |
| `events [prefix]` | List USP events | `usp events Device.` |
| `diff` | Show USP vs CWMP differences | `usp diff` |

### Path Conventions
- Objects end with `.` → `Device.WiFi.Radio.`
- Parameters have no trailing dot → `Device.WiFi.Radio.Channel`
- Commands display as `Name()` → `Reboot()`
- Events display as `Name!` → `Boot!`

## Workflow

When the user asks about TR-181:

1. Determine protocol context (USP or CWMP). If unclear, ask.
2. Run the lookup script to get exact data.
3. Return ONLY verified information from the data model.
4. When writing code that references TR-181 paths, verify EVERY path first.
5. If a path is not found, show search suggestions.

## Top-Level Objects

Device.ATM, Device.BASAPM, Device.Bridging, Device.BulkData, Device.CaptivePortal, Device.Cellular, Device.CollectionDevice, Device.ConnectionMonitoring, Device.DHCPv4, Device.DHCPv6, Device.DLNA, Device.DNS, Device.DOCSIS, Device.DSL, Device.DSLite, Device.DeviceInfo, Device.DynamicDNS, Device.Ethernet, Device.FAP, Device.FAST, Device.FWE, Device.FaultMgmt, Device.Firewall, Device.GRE, Device.GatewayInfo, Device.Ghn, Device.HPNA, Device.Hardware, Device.HomePlug, Device.Hosts, Device.IEEE1905, Device.IEEE8021x, Device.IP, Device.IPsec, Device.IPv6rd, Device.InterfaceStack, Device.IoTCapability, Device.L2TPv3, Device.LANConfigSecurity, Device.LEDs, Device.LLDP, Device.LMAP, Device.LocalAgent (USP only), Device.Logical, Device.MAP, Device.MQTT, Device.ManagementServer (CWMP only), Device.MoCA, Device.NAT, Device.NeighborDiscovery, Device.Node, Device.Optical, Device.PCP, Device.PPP, Device.PTM, Device.PeriodicFileTransfer, Device.PeriodicStatistics, Device.ProxiedDevice, Device.QoS, Device.RadSecProxy, Device.RouterAdvertisement, Device.Routing, Device.SFPs, Device.SSH, Device.STOMP, Device.Schedules, Device.Security, Device.Services, Device.SessionManagement, Device.SmartCardReaders, Device.SoftwareModules, Device.Syslog, Device.Thread, Device.Time, Device.TrustedElements, Device.UPA, Device.UPnP, Device.USB, Device.USPServices, Device.UnixDomainSockets, Device.UserInterface, Device.Users, Device.VXLAN, Device.WWC, Device.WiFi, Device.WireGuard, Device.XMPP, Device.XPON, Device.ZigBee

## Updating
To update to a newer data model version:
1. Download new HTML files from broadband-forum.org into `raw/`
2. Run `./rebuild.sh VERSION` (e.g. `./rebuild.sh 2-22-0`)
3. Upload the generated `tr-data-models.skill` to Claude Settings > Skills
