#!/usr/bin/env python3
"""Read a repository before you run it. Usage: python3 inspect-repo.py /path/to/repo"""
import collections, pathlib, re, sys

if len(sys.argv) != 2:
    print("usage: python3 inspect-repo.py /path/to/repo")
    raise SystemExit(2)
root = pathlib.Path(sys.argv[1]).expanduser()
if not root.is_dir():
    print(f"not a directory: {root}")
    raise SystemExit(1)

skip = {".git", "node_modules", "vendor", "dist", "build", ".venv", "__pycache__"}
files = [p for p in root.rglob("*") if p.is_file() and not any(part in skip for part in p.parts)]
suffixes = collections.Counter(p.suffix.lower() or "(none)" for p in files)
print(f"files: {len(files)}")
print("top level: " + ", ".join(sorted(p.name for p in root.iterdir() if p.name not in skip)[:20]))
readme = next((p for p in (root / "README.md", root / "README.rst", root / "README") if p.is_file()), None)
if readme:
    headings = [line.strip() for line in readme.read_text(encoding="utf-8", errors="replace").splitlines() if re.match(r"^#{1,3}\s", line.strip())]
    print(f"readme: {readme.name}")
    for heading in headings[:12]:
        print("  " + heading)
else:
    print("readme: none found")
print("languages: " + ", ".join(f"{suffix} {count}" for suffix, count in suffixes.most_common(6)))
print("largest source files:")
for path in sorted(files, key=lambda p: p.stat().st_size, reverse=True)[:5]:
    print(f"  {path.relative_to(root)}  {path.stat().st_size} bytes")
print("Next: read the entry point and the tests before you run anything. File names are not a security review.")
