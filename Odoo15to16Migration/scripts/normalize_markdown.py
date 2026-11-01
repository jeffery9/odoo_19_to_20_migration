#!/usr/bin/env python3
"""Normalize markdown block boundaries for strict renderers.

Inserts a single blank line at block transitions that CommonMark tolerates
without one but stricter renderers (Markdown.pl-family, some doc sites and
IDE previews) mishandle: paragraph→heading, heading→content, paragraph→list,
list→paragraph, paragraph↔table, list↔table, table→heading, and around code
fences. List items stay contiguous (no blank lines inside a list).
Idempotent; never touches fenced code or YAML frontmatter.
"""
import re
import sys

FENCE = re.compile(r'^\s*(```|~~~)')
HEADING = re.compile(r'^#{1,6}\s')
TABLE = re.compile(r'^\s*\|')
ITEM = re.compile(r'^(\s*)(?:[-*+]|\d+[.)])\s+')
CONT = re.compile(r'^\s{2,}\S')


def classify(line, prev_cls, in_fence):
    if FENCE.match(line):
        return 'FENCE'
    if in_fence:
        return 'CODE'
    if not line.strip():
        return 'BLANK'
    if HEADING.match(line):
        return 'HEADING'
    if TABLE.match(line):
        return 'TABLE'
    if ITEM.match(line):
        return 'ITEM'
    if prev_cls in ('ITEM', 'CONT') and CONT.match(line):
        return 'CONT'
    return 'PARA'


def needs_blank(prev, cur):
    if prev in (None, 'BLANK'):
        return False
    if cur == 'HEADING' and prev in ('PARA', 'ITEM', 'CONT', 'TABLE'):
        return True
    if cur == 'ITEM' and prev in ('PARA', 'HEADING', 'TABLE'):
        return True
    if cur == 'PARA' and prev in ('ITEM', 'CONT', 'TABLE', 'HEADING'):
        return True
    if cur == 'TABLE' and prev in ('PARA', 'ITEM', 'CONT', 'HEADING'):
        return True
    if cur in ('ITEM', 'PARA', 'TABLE', 'HEADING') and prev == 'TABLE' and cur != 'TABLE':
        return True
    if cur == 'FENCE' and prev in ('PARA', 'ITEM', 'CONT', 'TABLE', 'HEADING'):
        return True
    if prev == 'FENCE' and cur in ('PARA', 'ITEM', 'TABLE', 'HEADING'):
        return True
    return False


def normalize(text):
    lines = text.splitlines()
    out = []
    # protect frontmatter
    fm = []
    if lines and lines[0].strip() == '---':
        fm.append(lines[0])
        for ln in lines[1:]:
            fm.append(ln)
            if ln.strip() == '---':
                break
        lines = lines[len(fm):]
        out.extend(fm)
        out.append('')
    in_fence = False
    prev = None
    for ln in lines:
        cls = classify(ln, prev, in_fence)
        if cls == 'FENCE':
            in_fence = not in_fence
        if needs_blank(prev, cls):
            out.append('')
        out.append(ln)
        prev = cls if cls != 'BLANK' else 'BLANK'
    # collapse triple blanks
    res = []
    blank = 0
    for ln in out:
        if not ln.strip():
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        res.append(ln)
    return '\n'.join(res).rstrip('\n') + '\n'


if __name__ == '__main__':
    for path in sys.argv[1:]:
        src = open(path, encoding='utf-8').read()
        fixed = normalize(src)
        open(path, 'w', encoding='utf-8').write(fixed)
        print('normalized', path, f'({len(src.splitlines())} -> {len(fixed.splitlines())} lines)')
