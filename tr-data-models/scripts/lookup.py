#!/usr/bin/env python3
"""
TR-181 Data Model Lookup Tool
Usage:
  python3 lookup.py <protocol> <action> <query>

Protocol: usp | cwmp
Actions:
  get <path>         - Get full details of a specific path (exact match)
  children <path>    - List all direct children of an object path
  search <pattern>   - Search paths by substring (case-insensitive)
  tree <path>        - Show subtree under a path (objects only, max 3 levels)
  commands [path]    - List commands (optionally filtered by path prefix)
  events [path]      - List events (optionally filtered by path prefix)
  diff               - Show differences between USP and CWMP models

Examples:
  python3 lookup.py usp get Device.WiFi.Radio.{i}.Channel
  python3 lookup.py usp children Device.WiFi.
  python3 lookup.py usp search SSID
  python3 lookup.py cwmp tree Device.IP.
  python3 lookup.py usp commands Device.WiFi.
  python3 lookup.py usp events Device.
"""

import json
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_model(protocol):
    proto = protocol.lower()
    path = os.path.join(SCRIPT_DIR, f"tr181_{proto}.json")
    with open(path) as f:
        return json.load(f)

def get_path(model, path):
    """Get full details of a specific path."""
    for section in ['objects', 'parameters', 'commands', 'events']:
        for item in model.get(section, []):
            if item['path'] == path:
                return item
    return None

def children(model, parent_path):
    """List direct children of an object."""
    if not parent_path.endswith('.'):
        parent_path += '.'
    depth = parent_path.count('.')
    results = []
    for section in ['objects', 'parameters', 'commands', 'events']:
        for item in model.get(section, []):
            p = item['path']
            if p.startswith(parent_path):
                remainder = p[len(parent_path):]
                # Direct child: no more dots (for params/cmds/events) or exactly one trailing dot (for objects)
                if section == 'objects':
                    if remainder.count('.') == 1 and remainder.endswith('.'):
                        results.append((section[:-1], item))
                else:
                    if '.' not in remainder:
                        results.append((section[:-1], item))
    return results

def search(model, pattern):
    """Search all paths by substring."""
    pattern_lower = pattern.lower()
    results = []
    for section in ['objects', 'parameters', 'commands', 'events']:
        for item in model.get(section, []):
            if pattern_lower in item['path'].lower():
                results.append((section[:-1], item))
    return results

def tree(model, root_path, max_depth=3):
    """Show object subtree."""
    if not root_path.endswith('.'):
        root_path += '.'
    root_depth = root_path.count('.')
    results = []
    for o in model['objects']:
        if o['path'].startswith(root_path) or o['path'] == root_path:
            depth = o['path'].count('.') - root_depth
            if depth <= max_depth:
                results.append((depth, o))
    return results

def list_commands(model, prefix=""):
    results = []
    for c in model.get('commands', []):
        if c['path'].startswith(prefix):
            results.append(c)
    return results

def list_events(model, prefix=""):
    results = []
    for e in model.get('events', []):
        if e['path'].startswith(prefix):
            results.append(e)
    return results

def format_item(kind, item, verbose=True):
    """Format an item for display."""
    lines = []
    marker = {'object': 'OBJ', 'parameter': 'PAR', 'command': 'CMD', 'event': 'EVT'}.get(kind, kind.upper())
    lines.append(f"[{marker}] {item['path']}  ({item['type']})  access={item['access']}  ver={item.get('ver', '')}")
    if verbose:
        if item.get('desc'):
            lines.append(f"  desc: {item['desc']}")
        if item.get('enums'):
            lines.append(f"  enums: {', '.join(item['enums'])}")
        if item.get('default'):
            lines.append(f"  default: {item['default']}")
        if item.get('input'):
            lines.append(f"  input args:")
            for a in item['input']:
                lines.append(f"    - {a['name']} ({a['type']}) {a['access']}: {a.get('desc', '')[:200]}")
                if a.get('enums'):
                    lines.append(f"      enums: {', '.join(a['enums'])}")
        if item.get('output'):
            lines.append(f"  output args:")
            for a in item['output']:
                lines.append(f"    - {a['name']} ({a['type']}) {a['access']}: {a.get('desc', '')[:200]}")
                if a.get('enums'):
                    lines.append(f"      enums: {', '.join(a['enums'])}")
    return '\n'.join(lines)

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    protocol = sys.argv[1]
    action = sys.argv[2]
    query = sys.argv[3] if len(sys.argv) > 3 else ""

    model = load_model(protocol)

    if action == 'get':
        item = get_path(model, query)
        if item:
            # Determine kind from which section it's in
            kind = 'parameter'
            for section in ['objects', 'parameters', 'commands', 'events']:
                if item in model.get(section, []):
                    kind = section[:-1]
                    break
            print(format_item(kind, item))
        else:
            print(f"NOT FOUND: {query}")
            # Suggest close matches
            results = search(model, query.split('.')[-1] if '.' in query else query)
            if results:
                print(f"\nDid you mean:")
                for kind, item in results[:10]:
                    print(f"  {item['path']}")

    elif action == 'children':
        results = children(model, query)
        if results:
            print(f"Children of {query} ({len(results)} items):\n")
            for kind, item in results:
                print(format_item(kind, item, verbose=False))
        else:
            print(f"No children found for: {query}")

    elif action == 'search':
        results = search(model, query)
        print(f"Search '{query}': {len(results)} results\n")
        for kind, item in results[:50]:
            print(format_item(kind, item, verbose=False))
        if len(results) > 50:
            print(f"\n... and {len(results) - 50} more")

    elif action == 'tree':
        results = tree(model, query)
        if results:
            print(f"Object tree under {query}:\n")
            for depth, o in results:
                indent = "  " * depth
                print(f"{indent}{o['path']}  (ver {o.get('ver', '')})")
        else:
            print(f"No objects found under: {query}")

    elif action == 'commands':
        results = list_commands(model, query)
        print(f"Commands{' under ' + query if query else ''}: {len(results)}\n")
        for c in results:
            print(format_item('command', c))
            print()

    elif action == 'events':
        results = list_events(model, query)
        print(f"Events{' under ' + query if query else ''}: {len(results)}\n")
        for e in results:
            print(format_item('event', e))
            print()

    elif action == 'diff':
        usp = load_model('usp')
        cwmp = load_model('cwmp')
        usp_paths = set()
        cwmp_paths = set()
        for section in ['objects', 'parameters', 'commands', 'events']:
            for item in usp.get(section, []):
                usp_paths.add(item['path'])
            for item in cwmp.get(section, []):
                cwmp_paths.add(item['path'])
        only_usp = usp_paths - cwmp_paths
        only_cwmp = cwmp_paths - usp_paths
        print(f"USP-only paths: {len(only_usp)}")
        for p in sorted(only_usp)[:30]:
            print(f"  + {p}")
        if len(only_usp) > 30:
            print(f"  ... and {len(only_usp) - 30} more")
        print(f"\nCWMP-only paths: {len(only_cwmp)}")
        for p in sorted(only_cwmp)[:30]:
            print(f"  + {p}")
        if len(only_cwmp) > 30:
            print(f"  ... and {len(only_cwmp) - 30} more")

    else:
        print(f"Unknown action: {action}")
        print(__doc__)

if __name__ == "__main__":
    main()
