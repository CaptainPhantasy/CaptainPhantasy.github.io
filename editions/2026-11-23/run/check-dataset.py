#!/usr/bin/env python3
"""Check a JSONL chat file before you spend GPU hours training. Read-only."""
import json
import pathlib
import sys


def messages_of(row):
    if not isinstance(row, dict):
        return None
    if isinstance(row.get("messages"), list):
        return row["messages"]
    if isinstance(row.get("prompt"), list):
        return row["prompt"] + (row.get("completion") or [])
    return None


def problem(line):
    try:
        row = json.loads(line)
    except ValueError as exc:
        return f"not valid JSON ({exc.msg})"
    messages = messages_of(row)
    if not messages:
        return "no messages list"
    for message in messages:
        if not isinstance(message, dict) or not isinstance(message.get("content"), str) or not message["content"].strip():
            return "a message has no text content"
    roles = [message.get("role") for message in messages]
    if "assistant" not in roles:
        return "no assistant turn"
    if roles[-1] != "assistant":
        return "last message is not the assistant"
    return ""


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: check-dataset.py train.jsonl")
    path = pathlib.Path(sys.argv[1])
    lines = [(number, line) for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1) if line.strip()]
    problems, sizes = [], []
    for number, line in lines:
        issue = problem(line)
        if issue:
            problems.append(f"line {number}: {issue}")
        else:
            sizes.append(sum(len(message["content"].split()) for message in messages_of(json.loads(line))))
    print(f"examples: {len(lines) - len(problems)} of {len(lines)} non-empty lines")
    if sizes:
        print(f"words per example: {min(sizes)} to {max(sizes)}")
    print(f"problems: {len(problems)}")
    for item in problems:
        print(item)


if __name__ == "__main__":
    main()
