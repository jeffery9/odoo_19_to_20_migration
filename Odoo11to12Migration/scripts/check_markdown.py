#!/usr/bin/env python3
"""Markdown compatibility linter for the skill docs (strict-renderer safe).

Checks (CommonMark/GFM + strict-renderer hygiene):
 1. pipe '|' inside inline code spans inside table rows (must be \\|) — splits columns
 2. inconsistent table column counts within one table
 3. raw HTML-looking tags (<tree>, <record …/>) outside code spans/fences
 4. block boundaries without a blank line (heading/list/table/fence after
    paragraph or list; paragraph after list/table; content right after heading)
 5. unbalanced code fences
 6. accidental links: [text]( directly outside code
Usage: python3 check_markdown.py FILE...   (exit 1 on findings)
"""
import re
import sys

CODE_SPAN = re.compile(r'(`+)(.*?)\1', re.S)
FENCE = re.compile(r'^\s*(```|~~~)')
HEADING = re.compile(r'^#{1,6}\s')
TABLE = re.compile(r'^\s*\|')
ITEM = re.compile(r'^(\s*)(?:[-*+]|\d+[.)])\s+')
CONT = re.compile(r'^\s{2,}\S')
RAW_TAG = re.compile(r'<[A-Za-z][^<>*`\n]{0,80}?/?>')
LINKISH = re.compile(r'\[[^\]\n]{1,60}\]\(')


def strip_code(line):
    spans = []
    def sub(m):
        spans.append(m.group(2))
        return '\x00%d\x00' % (len(spans) - 1)
    return CODE_SPAN.sub(sub, line), spans


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


def check(path):
    issues = []
    lines = open(path, encoding='utf-8').read().splitlines()
    # skip frontmatter
    start = 0
    if lines and lines[0].strip() == '---':
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                start = i + 1
                break
    in_fence = False
    prev = None
    prev_no = 0
    table_cols = None
    table_start = 0
    for no, raw in enumerate(lines[start:], start + 1):
        cls = classify(raw, prev, in_fence)
        if cls == 'FENCE':
            in_fence = not in_fence
        if cls in ('FENCE', 'CODE'):
            prev, prev_no = cls, no
            continue
        plain, spans = strip_code(raw)
        if cls == 'TABLE':
            for s in spans:
                if '|' in s and '\\|' not in s:
                    issues.append((no, 'pipe-in-code-in-table', s[:60]))
            n = plain.count('|')
            if table_cols is None:
                table_cols, table_start = n, no
            elif n != table_cols:
                issues.append((no, 'table-column-count', f'{n} pipes vs {table_cols} (table@{table_start})'))
        else:
            table_cols = None
            if cls == 'HEADING' and prev in ('PARA', 'ITEM', 'CONT', 'TABLE'):
                issues.append((no, 'missing-blank-line', f'before heading (after L{prev_no})'))
            if cls == 'ITEM' and prev in ('PARA', 'HEADING', 'TABLE'):
                issues.append((no, 'missing-blank-line', f'before list (after L{prev_no})'))
            if cls == 'PARA' and prev in ('ITEM', 'CONT', 'TABLE', 'HEADING'):
                issues.append((no, 'missing-blank-line', f'before paragraph (after L{prev_no})'))
            if cls == 'TABLE' and prev in ('PARA', 'ITEM', 'CONT', 'HEADING'):
                issues.append((no, 'missing-blank-line', f'before table (after L{prev_no})'))
            if cls == 'FENCE' and prev in ('PARA', 'ITEM', 'CONT', 'TABLE', 'HEADING'):
                issues.append((no, 'missing-blank-line', f'before fence (after L{prev_no})'))
            if cls in ('PARA', 'ITEM', 'TABLE', 'HEADING') and prev == 'FENCE':
                issues.append((no, 'missing-blank-line', f'after fence (before L{no})'))
            if cls not in ('TABLE',):
                for m in RAW_TAG.finditer(plain):
                    issues.append((no, 'raw-html-tag', m.group(0)[:50]))
                for m in LINKISH.finditer(plain):
                    issues.append((no, 'accidental-link', m.group(0)[:50]))
        prev, prev_no = cls, no
    if in_fence:
        issues.append((len(lines), 'unbalanced-fence', ''))
    return issues


def main():
    bad = 0
    for path in sys.argv[1:]:
        issues = check(path)
        print(f'== {path}: {len(issues)} issue(s)')
        for no, kind, txt in issues:
            print(f'   L{no:<4} {kind}: {txt}')
        bad += len(issues)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
