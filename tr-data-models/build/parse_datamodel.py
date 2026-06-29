#!/usr/bin/env python3
"""
TR-181 Data Model Parser — converts Broadband Forum HTML to structured JSON.
Usage: python3 parse_datamodel.py <usp_html> <cwmp_html> <output_dir> [--version VER]
"""
import json, re, os, sys, argparse
from bs4 import BeautifulSoup

def clean_text(el):
    if el is None: return ""
    return re.sub(r'\s+', ' ', el.get_text(separator=' ')).strip()

def parse_row(tr):
    cells = tr.find_all('td', recursive=False)
    if len(cells) < 4: return None
    name_span = cells[0].find('span', id=True)
    raw_name = clean_text(cells[0])
    full_id = name_span.get('id', '') if name_span else ''
    path = re.sub(r'^D\.Device:\d+\.', '', full_id) if full_id else ''
    type_text = clean_text(cells[1])
    access = clean_text(cells[2])
    desc = clean_text(cells[3])
    if len(desc) > 500: desc = desc[:497] + "..."
    default_val = clean_text(cells[4]) if len(cells) > 4 else "-"
    version = clean_text(cells[5]) if len(cells) > 5 else ""
    enums = []
    for li in cells[3].find_all('li'):
        li_span = li.find('span', id=True)
        if li_span: enums.append(clean_text(li_span))
    entry = {"path": path, "name": raw_name.lstrip('\u21d2 ').strip(), "type": type_text, "access": access, "desc": desc, "ver": version}
    if default_val and default_val != "-": entry["default"] = default_val
    if enums: entry["enums"] = enums
    return entry

def parse_file(filepath, protocol, version):
    print(f"Parsing {filepath}...")
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        soup = BeautifulSoup(f, 'lxml')
    all_trs = soup.find_all('tr', class_=re.compile(r'^(object|parameter|command|event|argument-container|argument-parameter|argument-object)'))
    start_idx = 0
    for i, tr in enumerate(all_trs):
        cls = tr.get('class', []); cls = [cls] if isinstance(cls, str) else cls
        if 'object' in cls:
            span = tr.find('span', id=True)
            if span and 'Device.' in span.get('id', ''): start_idx = i; break
    all_trs = all_trs[start_idx:]
    objects, parameters, commands, events = [], [], [], []
    current, kind, direction = None, None, None
    def flush():
        nonlocal current, kind, direction
        if current:
            if not current['input']: del current['input']
            if not current['output']: del current['output']
            (commands if kind == 'command' else events).append(current)
        current, kind, direction = None, None, None
    for tr in all_trs:
        cls = tr.get('class', []); cls = [cls] if isinstance(cls, str) else cls
        rt = cls[0] if cls else ''
        if rt in ('object','parameter','command','event'):
            flush(); entry = parse_row(tr)
            if not entry: continue
            if rt == 'object': objects.append(entry)
            elif rt == 'parameter': parameters.append(entry)
            elif rt in ('command','event'):
                kind = rt; entry['input'],entry['output'] = [],[]
                current = entry; direction = 'output' if rt == 'event' else 'input'
        elif rt == 'argument-container':
            raw = clean_text(tr)
            if 'Input' in raw: direction = 'input'
            elif 'Output' in raw: direction = 'output'
        elif rt in ('argument-parameter','argument-object'):
            if current and direction:
                entry = parse_row(tr)
                if entry: current[direction].append(entry)
    flush()
    model = {"protocol": protocol, "model": f"tr-181-{version}",
             "stats": {"objects": len(objects), "parameters": len(parameters), "commands": len(commands), "events": len(events)},
             "objects": objects, "parameters": parameters}
    if commands: model["commands"] = commands
    if events: model["events"] = events
    c_args = sum(1 for c in commands if 'input' in c or 'output' in c)
    e_args = sum(1 for e in events if 'input' in e or 'output' in e)
    print(f"  Objects: {len(objects)}, Params: {len(parameters)}, Cmds: {len(commands)} ({c_args} with args), Evts: {len(events)} ({e_args} with args)")
    return model

def main():
    p = argparse.ArgumentParser()
    p.add_argument('usp_html'); p.add_argument('cwmp_html'); p.add_argument('output_dir')
    p.add_argument('--version', default='2-21-0')
    args = p.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    usp = parse_file(args.usp_html, "USP", args.version)
    cwmp = parse_file(args.cwmp_html, "CWMP", args.version)
    for name, data in [("tr181_usp.json", usp), ("tr181_cwmp.json", cwmp)]:
        path = os.path.join(args.output_dir, name)
        with open(path, 'w') as f: json.dump(data, f, separators=(',',':'))
        print(f"{path}: {os.path.getsize(path)/(1024*1024):.1f} MB")

if __name__ == "__main__": main()
