#!/usr/bin/env python3
"""Mine verified deltas between two refs of a GitHub repo (pipeline B).

Fetches raw files from both refs and prints markdown-ready diffs:
  --kind defs      module-level + method def names removed/added
  --kind classes   class names removed/added
  --kind exports   names re-exported via import statements (ast)
  --grep PATTERN   occurrence counts per ref + first matching lines
Usage:
  python3 branch_diff.py --repo odoo/odoo --a 19.0 --b 20.0 \
      --pairs "odoo/orm/models.py:odoo/orm/models.py,odoo/tools/__init__.py:odoo/tools/__init__.py" \
      --kind defs
A 404 on one side is reported as removed/added file (path-level delta).
"""
import argparse
import ast
import re
import urllib.request

RAW = 'https://raw.githubusercontent.com/{repo}/{ref}/{path}'


def fetch(repo, ref, path):
    try:
        return urllib.request.urlopen(RAW.format(repo=repo, ref=ref, path=path)).read().decode()
    except Exception:
        return None


def defs(src):
    return set(re.findall(r'\n(?:    )?(?:async )?def ([a-zA-Z_][a-zA-Z0-9_]*)\(', src))


def classes(src):
    return set(re.findall(r'\nclass ([a-zA-Z_][a-zA-Z0-9_]*)', src))


def exports(src):
    names = set()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return names
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            for a in n.names:
                names.add(a.asname or a.name)
        elif isinstance(n, ast.Import):
            for a in n.names:
                names.add((a.asname or a.name).split('.')[0])
    return names


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repo', default='odoo/odoo')
    ap.add_argument('--a', required=True, help='old ref')
    ap.add_argument('--b', required=True, help='new ref')
    ap.add_argument('--pairs', required=True, help='comma list of old_path:new_path')
    ap.add_argument('--kind', choices=['defs', 'classes', 'exports', 'grep'], default='defs')
    ap.add_argument('--pattern', default='')
    args = ap.parse_args()

    fn = {'defs': defs, 'classes': classes, 'exports': exports}[args.kind] if args.kind != 'grep' else None
    for pair in args.pairs.split(','):
        pa, pb = (pair.split(':') + [pair.split(':')[0]])[:2] if ':' in pair else (pair, pair)
        a, b = fetch(args.repo, args.a, pa), fetch(args.repo, args.b, pb)
        print(f'## {pa} ({args.a})  →  {pb} ({args.b})')
        if a is None or b is None:
            print('   file-level delta: present in a=%s b=%s' % (a is not None, b is not None))
            continue
        if args.kind == 'grep':
            ra = re.findall(r'.*%s.*' % re.escape(args.pattern), a)
            rb = re.findall(r'.*%s.*' % re.escape(args.pattern), b)
            print(f'   matches: {args.a}={len(ra)} {args.b}={len(rb)}')
            for l in rb[:6]:
                print('   b:', l.strip()[:100])
            continue
        sa, sb = fn(a), fn(b)
        removed, added = sorted(sa - sb), sorted(sb - sa)
        print('   removed (%d): %s' % (len(removed), ', '.join(f'`{x}`' for x in removed) or '—'))
        print('   added   (%d): %s' % (len(added), ', '.join(f'`{x}`' for x in added) or '—'))


if __name__ == '__main__':
    main()
