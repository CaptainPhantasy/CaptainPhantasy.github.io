#!/usr/bin/env python3
"""Report which model providers are configured, without printing secrets.

Usage:
  python3 check-model-route.py
  python3 check-model-route.py --probe
  python3 check-model-route.py --env-file ~/.env.local --probe
"""
import argparse, json, os, pathlib, re, urllib.parse, urllib.request

def load_env(path):
    values = dict(os.environ)
    if path:
        p = pathlib.Path(path).expanduser()
        if p.is_file():
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line.strip())
                if m and m.group(1) not in values:
                    values[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return values

def host(url):
    try:
        return urllib.parse.urlsplit(url).hostname or url
    except Exception:
        return "(invalid URL)"

def probe(base, key):
    url = base.rstrip("/") + "/models"
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            body = json.load(response)
        return ", ".join(str(item.get("id", "?")) for item in body.get("data", [])[:8]) or "(no models listed)"
    except Exception as exc:
        return f"probe failed: {type(exc).__name__}"

parser = argparse.ArgumentParser()
parser.add_argument("--env-file", default="~/.env.local")
parser.add_argument("--probe", action="store_true")
args = parser.parse_args()
env = load_env(args.env_file)

providers = {}
for name, value in env.items():
    m = re.match(r"^([A-Z0-9]+)_BASE_URL$", name)
    if m:
        providers.setdefault(m.group(1), {})["base"] = value
    m = re.match(r"^([A-Z0-9]+)_API_KEY$", name)
    if m:
        providers.setdefault(m.group(1), {})["key"] = value

if not providers:
    print("No provider variables found. Expected a NAME_BASE_URL and NAME_API_KEY pair.")
    raise SystemExit(0)

print("provider      key        base host")
for name in sorted(providers):
    item = providers[name]
    print(f"{name.lower():<13} {'present' if item.get('key') else 'missing':<10} {host(item.get('base', ''))}")
    if args.probe and item.get("key") and item.get("base"):
        print(f"  models: {probe(item['base'], item['key'])}")
print("\nNo key values were printed.")
