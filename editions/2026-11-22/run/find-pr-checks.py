#!/usr/bin/env python3
"""List workflow lines that may be polling GitHub. Local, read-only; no CLI login."""
import argparse
import pathlib
import re

CHECK = re.compile(r'\bgh\s+(?:pr\s+(?:view|checks)|run\s+(?:view|watch))\b')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', type=pathlib.Path)
    root = parser.parse_args().repository.resolve(strict=True)
    workflows = root / '.github' / 'workflows'
    hits = 0
    for path in sorted(workflows.glob('*')):
        if (path.suffix.lower() not in ('.yml', '.yaml') or not path.is_file() or
                not path.resolve().is_relative_to(root) or path.stat().st_size > 1_000_000):
            continue
        for number, line in enumerate(path.read_text(errors='replace').splitlines(), 1):
            if not line.lstrip().startswith('#') and (match := CHECK.search(line)):
                print(f'{path.relative_to(root)}:{number}: {match.group()}')
                hits += 1
    print(f'candidate lines: {hits}')


if __name__ == '__main__':
    main()
