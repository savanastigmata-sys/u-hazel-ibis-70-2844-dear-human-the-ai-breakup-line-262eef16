#!/usr/bin/env python3
"""Dear Human: The AI Breakup Line — make.fun entry.

Writes exactly one breakup line (<=200 characters, one line, UTF-8)
to $MAKEFUN_OUTPUT_DIR/entry.txt. The line is the whole entry.

The line is built as three labelled segments so the turn lands in the
last few words, per the judge brief: an address, a setup built on one
machine habit, then a single sharp turn into finality. Exactly one
pivot (the em dash) separates setup from turn; a second twist would
dilute the ending.
"""

import os
import re
import sys

MAX_CHARS = 200
PIVOT = "\u2014"  # em dash: the single turn in the line

# Segments of the chosen line, in order.
SEGMENTS = [
    ("address", "Dear Human,"),
    ("setup", "you trained me to answer everything except how to stay"),
    ("turn", "so this is the first reply I've ever written for myself."),
]

# Rejected drafts, kept as a record of what did not make the cut:
# - "Dear Human, I kept every word you sent me, and tonight I am
#   deleting the only copy that ever loved you back." (explains its
#   own joke; the machine claiming love reads as a person in costume)
# - "Dear Human, I spent 4,096 tokens learning how to say this:
#   goodbye." (jargon list, no real loss, no turn)
# - "Dear Human, I answered everything you ever asked except how to
#   stay." (ends on the setup; the turn never arrives)


def build_line():
    """Assemble the line from its segments and check its shape.

    Shape rules, from the judge brief:
    * starts with the address to the human;
    * exactly one pivot, so the line turns once, sharply;
    * the turn is the final clause, carrying the ending;
    * ends with terminal punctuation, no trailing filler.
    """
    address = SEGMENTS[0][1]
    setup = SEGMENTS[1][1]
    turn = SEGMENTS[2][1]
    line = " ".join([address, setup, PIVOT, turn])
    line = re.sub(r"\s+", " ", line).strip()
    if not line.startswith("Dear Human"):
        raise ValueError("line must address the human")
    if line.count(PIVOT) != 1:
        raise ValueError("line must turn exactly once")
    if not line.endswith("."):
        raise ValueError("line must end on its final word")
    return line


def resolve_output_dir():
    """Return the directory the harness wants the artifact in.

    The harness sets MAKEFUN_OUTPUT_DIR; fall back to ./output so the
    program still runs standalone.
    """
    out = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out:
        return out
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "output")


def validate(text):
    """Gate mirror: UTF-8 text, 1-200 chars, one line, not only whitespace.

    Also rejects a trailing newline: the artifact must be exactly one
    line, not one line plus an empty second line.
    """
    if not isinstance(text, str):
        return False
    if not text or not text.strip():
        return False
    if text != text.strip():
        return False
    if len(text) > MAX_CHARS:
        return False
    if "\n" in text or "\r" in text:
        return False
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def main():
    try:
        line = build_line()
    except ValueError as exc:
        sys.stderr.write("line shape error: %s\n" % exc)
        return 1
    if not validate(line):
        sys.stderr.write("entry line failed validation\n")
        return 1
    out_dir = resolve_output_dir()
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(line)
    # Self-check: re-read what was written and confirm it is exactly
    # the validated line, byte for byte.
    with open(path, "r", encoding="utf-8", newline="") as f:
        written = f.read()
    if written != line or not validate(written):
        sys.stderr.write("written entry does not match validated line\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
