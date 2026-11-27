#!/usr/bin/env python3
"""Print the Ruby, Rails and Bundler versions a project actually runs."""
import pathlib
import platform
import shutil
import subprocess
import sys


def version(label, command):
    if not shutil.which(command):
        return f"  {label}: not found"
    try:
        result = subprocess.run([command, "--version"], capture_output=True, text=True, timeout=10)
        line = (result.stdout or result.stderr).strip().splitlines()[0]
        if "not currently installed" in line:
            return f"  {label}: not found"
        return f"  {label}: {line}"
    except Exception as exc:
        return f"  {label}: error ({type(exc).__name__})"


root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve(strict=True)
print("project:")
for name in ("Gemfile", "Gemfile.lock"):
    print(f"  {name}: {'found' if (root / name).is_file() else 'absent'}")
lock = root / "Gemfile.lock"
if lock.is_file():
    lines = lock.read_text(errors="replace").splitlines()
    for number, line in enumerate(lines):
        text = line.strip()
        if text.startswith("rails ("):
            print(f"  rails: {text[7:-1]} (Gemfile.lock)")
        elif text == "RUBY VERSION" and number + 1 < len(lines):
            print(f"  ruby: {lines[number + 1].strip().removeprefix('ruby ').strip()} (Gemfile.lock)")

print("toolchain:")
print(f"  os: {platform.system()} {platform.release()} ({platform.machine()})")
for label, command in (("ruby", "ruby"), ("rails", "rails"), ("bundle", "bundle")):
    print(version(label, command))
