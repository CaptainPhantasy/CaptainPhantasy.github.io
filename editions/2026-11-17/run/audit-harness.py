#!/usr/bin/env python3
"""Read-only audit of editor harness settings.

Scans the default settings paths for VS Code, Insiders, Cursor, and VSCodium.
Prints only keys whose names contain "harness" or "sessiontarget". It never
prints the whole settings file and never writes anything.
"""
import os
import pathlib
import platform
import re
import sys

HOME = pathlib.Path.home()
EDITORS = ["Code", "Code - Insiders", "Cursor", "VSCodium"]
PATTERN = re.compile(
    r'"([^"]*(?:harness|sessiontarget)[^"]*)"\s*:\s*'
    r'("(?:[^"\\]|\\.)*"|true|false|null)',
    re.IGNORECASE,
)


def settings_paths():
    paths = []
    for name in EDITORS:
        if os.name == "nt":
            appdata = pathlib.Path(os.environ.get("APPDATA", HOME / "AppData/Roaming"))
            paths.append(appdata / name / "User" / "settings.json")
        elif platform.system() == "Darwin":
            paths.append(
                HOME / "Library/Application Support" / name / "User" / "settings.json"
            )
        else:
            paths.append(HOME / ".config" / name / "User" / "settings.json")
    return paths


def main():
    scanned = 0
    with_keys = 0
    for path in settings_paths():
        if not path.is_file():
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"{path}: cannot read ({type(exc).__name__})")
            continue
        matches = PATTERN.findall(text)
        print(path)
        if not matches:
            print("  no harness-related keys")
            continue
        with_keys += 1
        for key, value in matches:
            print(f"  {key} = {value}")

    if not scanned:
        print("No editor settings files found.")
        return 1

    print(f"\nScanned {scanned} settings file(s); {with_keys} had harness-related keys.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
