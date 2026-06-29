#!/usr/bin/env python3
"""
TR-181 Data Model Parser
Converts Broadband Forum HTML data model pages into structured JSON.

Usage:
  python3 parse_datamodel.py <usp_html> <cwmp_html> <output_dir> [--version VERSION]

Example:
  python3 parse_datamodel.py raw/tr-181-2-21-0-usp.htm raw/tr-181-2-21-0-cwmp.htm . --version 2-21-0
"""

import json
import re
import os
import sys
import argparse
from bs4 import BeautifulSoup


def clean_text(el):
    if el is None:
        return ""
    return re.sub(r'\s+', ' ', el.get_text(separator=' ')).strip()


def parse_row(tr):
    cells = tr.find_all('td', recursive=False)
    if len(cells) < 4:
        return None

    name_span = cells[0].find('span', id=True)
    raw_name = clean_text(cells[0])
    full_id = name_span.get('id', '') if name_span else ''
    path = re.sub(r'^D\.Device:\d+\.', '', full_id) if full_id else ''

    type_text = clean_text(cells[1])
    access = clean_text(cells[2])
    desc = clean_text(cells[3])
    if len(desc) > 500:
        desc = desc[:497] + "..."
    default_val = clean_text(cells[4]) if len(cells) > 4 else "-"
    version = clean_text(cells[5]) if len(cells) > 5 else ""

    enums = []
    for li in cells[3].find_all('li'):
        li_span = li.find('span', id=True)
        if li_span:
            enums.append(clean_text(li_span))

    entry = {
        "path": path,
        "name": raw_name.lstrip('\u21d2 ').strip(),
        "type": type_text,
        "access": access,
        "desc": desc,
        "ver": version,
    }
    if default_val and default_val != "-":
        entry["default"] = default_val
    if enums:
        entry["enums"] = enums

    return entry


def parse_file(filepath, protocol, model_version):
    print(f"Parsing {filepath}...")
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        soup = BeautifulSoup(f, 'lxml')

    all_trs = soup.find_all('tr', class_=re.compile(
        r'^(object|parameter|command|event|argument-container|argument-parameter|argument-object)'))

    # Skip legend rows - find first actual Device. object
    start_idx = 0
    for i, tr in enumerate(all_trs):
        cls = tr.get('class', [])
        if isinstance(cls, str):
            cls = [cls]
        if 'object' in cls:
            span = tr.find('span', id=True)
            if span and 'Device.' in span.get('id', ''):
                start_idx = i
                break
    all_trs = all_trs[start_idx:]
    print(f"  Processing {len(all_trs)} rows")

    objects, parameters, commands, events = [], [], [], []
    current_cmd_or_evt, current_kind, current_direction = None, None, None

    def flush():
        nonlocal current_cmd_or_evt, current_kind, current_direction
        if current_cmd_or_evt:
            if not current_cmd_or_evt['input']:
                del current_cmd_or_evt['input']
            if not current_cmd_or_evt['output']:
                del current_cmd_or_evt['output']
            (commands if current_kind == 'command' else events).append(current_cmd_or_evt)
        current_cmd_or_evt, current_kind, current_direction = None, None, None

    for tr in all_trs:
        cls = tr.get('class', [])
        if isinstance(cls, str):
            cls = [cls]
        row_type = cls[0] if cls else ''

        if row_type in ('object', 'parameter', 'command', 'event'):
            flush()
            entry = parse_row(tr)
            if not entry:
                continue
            if row_type == 'object':
                objects.append(entry)
            elif row_type == 'parameter':
                parameters.append(entry)
            elif row_type in ('command', 'event'):
                current_kind = row_type
                entry['input'], entry['output'] = [], []
                current_cmd_or_evt = entry
                current_direction = 'output' if row_type == 'event' else 'input'

        elif row_type == 'argument-container':
            raw = clean_text(tr)
            if 'Input' in raw:
                current_direction = 'input'
            elif 'Output' in raw:
                current_direction = 'output'

        elif row_type in ('argument-parameter', 'argument-object'):
            if current_cmd_or_evt and current_direction:
                entry = parse_row(tr)
                if entry:
                    current_cmd_or_evt[current_direction].append(entry)

    flush()

    model = {
        "protocol": protocol,
        "model": f"tr-181-{model_version}",
        "stats": {
            "objects": len(objects),
            "parameters": len(parameters),
            "commands": len(commands),
            "events": len(events),
        },
        "objects": objects,
        "parameters": parameters,
    }
    if commands:
        model["commands"] = commands
    if events:
        model["events"] = events

    cmds_with_args = sum(1 for c in commands if 'input' in c or 'output' in c)
    evts_with_args = sum(1 for e in events if 'input' in e or 'output' in e)
    print(f"  Objects: {len(objects)}, Params: {len(parameters)}, "
          f"Cmds: {len(commands)} ({cmds_with_args} with args), "
          f"Evts: {len(events)} ({evts_with_args} with args)")
    return model


def main():
    parser = argparse.ArgumentParser(description='Parse TR-181 HTML data model files into JSON')
    parser.add_argument('usp_html', help='Path to USP HTML file')
    parser.add_argument('cwmp_html', help='Path to CWMP HTML file')
    parser.add_argument('output_dir', help='Output directory for JSON files')
    parser.add_argument('--version', default='2-21-0', help='Model version string (default: 2-21-0)')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    usp = parse_file(args.usp_html, "USP", args.version)
    cwmp = parse_file(args.cwmp_html, "CWMP", args.version)

    usp_path = os.path.join(args.output_dir, "tr181_usp.json")
    cwmp_path = os.path.join(args.output_dir, "tr181_cwmp.json")

    with open(usp_path, 'w') as f:
        json.dump(usp, f, separators=(',', ':'))
    with open(cwmp_path, 'w') as f:
        json.dump(cwmp, f, separators=(',', ':'))

    for fn in [usp_path, cwmp_path]:
        size = os.path.getsize(fn) / (1024 * 1024)
        print(f"{fn}: {size:.1f} MB")

    print(f"\nDone. Model version: tr-181-{args.version}")
    print(f"USP: {usp['stats']}")
    print(f"CWMP: {cwmp['stats']}")


if __name__ == "__main__":
    main()
