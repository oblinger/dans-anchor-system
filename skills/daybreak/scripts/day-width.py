#!/usr/bin/env python3
"""Rendered width of a Lumen Day bullet — what Obsidian actually lays out.

Markdown syntax is invisible in the render, so source length is the wrong ruler.
Strips **bold**, *italic*, `code`, [[wiki|links]] (display text survives), and the
leading "- ". Emoji are counted as 2 columns, which is how they lay out.
"""
import re, sys, unicodedata

LIMIT = 72

def rendered(line):
    s = re.sub(r'^\s*-\s+', '', line.rstrip())
    s = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', s)   # [[target|display]] -> display
    s = re.sub(r'\[\[([^\]]*)\]\]', r'\1', s)            # [[name]] -> name
    s = s.replace('**', '').replace('`', '')
    s = re.sub(r'(?<!\*)\*(?!\*)', '', s)
    w = 0
    for ch in s:
        w += 2 if unicodedata.east_asian_width(ch) in ('W', 'F') or ord(ch) > 0x2100 else 1
    return w, s

def main(path):
    bad = 0
    for n, line in enumerate(open(path), 1):
        if not line.lstrip().startswith('- '):
            continue
        w, s = rendered(line)
        if w > LIMIT:
            bad += 1
            print(f"  line {n}: {w} cols (>{LIMIT})  {s[:80]}")
    print(f"{'OK — no bullet wraps' if not bad else f'{bad} bullet(s) will wrap'}")
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else 'Lumen Day.md'))
