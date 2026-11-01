#!/usr/bin/env python3
"""Scaffold a new migration agent skill (pipeline D).

Creates:
  <dir>/SKILL.md            frontmatter + workflow skeleton (house conventions)
  <dir>/README.md           install/use instructions
  <dir>/references/01-mapping.md   table template with provenance column
  <dir>/scripts/scanner.py  pattern-table scanner skeleton (stdlib, exit 1 on findings)
  <dir>/scripts/check_markdown.py, normalize_markdown.py  (copied from this forge)
Usage:
  python3 skill_scaffold.py --dir /path/NewSkill --name my_migration \
      --title "My 1→2 Migration" --versions "1.0,2.0" \
      --description "Use when migrating X from 1 to 2 ..."
"""
import argparse
import shutil
from pathlib import Path

SKILL_TMPL = """---
name: {name}
description: {description}
version: 0.1.0
author: {author}
category: migration
odoo_versions: [{versions_q}]
tags: [{tags}]
---

# {title}

## Goal
Take a {old} custom addon/codebase to {new} with no leftover old-version API,
using automated codemods first and verified manual mappings second.

## Sources (authoritative)
- `references/*.md` in this skill (source-verified tables; provenance column per row).
- Upstream trees: branch `{old}` and `{new}` of the product repository.
- Bundled codemods of the product, if any (record commands in a reference file).
- Items tagged **[EE-verify]** (or vendor-private) must be re-checked against the
  private tree before deployment; never present them as verified.

## Workflow
1. **Triage** — `python3 scripts/scanner.py /path/to/code` (add `--json`); read the report.
2. **Codemod first** — run the product's bundled codemods on a clean branch, dry-run first;
   review the diff and commit.
3. **Manual mappings** — apply replacements from `references/01-mapping.md` (extend per topic).
4. **Validate** — re-run the scanner (expect 0), then update + run the test suite.
5. **Report** — codemod changes, manual edits with reference anchors, private-tree items, tests.

## Hard rules
- Do not invent identifiers: look them up in the `{new}` tree or cite the mapping table.
- Every completed/clipped value records its provenance tier (doc / public source / reconstruction).
- Markdown stays strict-renderer safe: `check_markdown.py` must report 0 issues.
"""

README_TMPL = """# {title} — agent skill

## Install
Copy this folder into your plugin/skills directory (e.g. `plugin/skills/` of
odoo-agent-pro-kit, or `~/.claude/skills/`).

## Use
1. `python3 scripts/scanner.py /path/to/code`
2. Ask the agent to migrate using the `{name}` skill.

## QA
`python3 scripts/check_markdown.py SKILL.md README.md references/*.md` → 0 issues.
"""

REF_TMPL = """# Mapping tables ({old} → {new})

Provenance column: `src` = verified in `{new}` tree (cite file), `doc` = corpus,
`rec` = reconstruction (flag in changelog), `EE` = private tree, needs review.

| {old} | {new} | provenance |
|---|---|---|
| `example.old_api()` | `example.new_api()` | src: path/to/file.py |
"""

SCANNER_TMPL = '''#!/usr/bin/env python3
"""Scanner skeleton: fill PATTERNS with (id, extensions, regex, mode, fix, reference).
mode: 'auto' = a bundled codemod fixes it, 'manual' = hand edit. Exit 1 on findings."""
import argparse, json, re, sys
from pathlib import Path

PATTERNS = [
    # ('old-api', {'py'}, re.compile(r'\\\\bold_api\\\\('), 'manual',
    #  'new_api() (see references/01-mapping.md)', '01-mapping.md'),
]
EXT = {'.py': 'py', '.xml': 'xml', '.csv': 'csv', '.js': 'js'}


def scan(root):
    out = []
    for p in sorted(root.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:
            continue
        ext = EXT.get(p.suffix)
        if not ext:
            continue
        text = p.read_text(encoding='utf-8', errors='ignore')
        for pid, exts, rx, mode, fix, ref in PATTERNS:
            if ext not in exts:
                continue
            for m in rx.finditer(text):
                out.append({'file': str(p), 'line': text.count(chr(10), 0, m.start()) + 1,
                            'id': pid, 'mode': mode, 'fix': fix, 'ref': ref})
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    f = scan(Path(a.root))
    print(json.dumps(f, indent=1) if a.json else
          '\\n'.join(f"{x['file']}:{x['line']} [{x['mode']}] {x['id']} -> {x['fix']}" for x in f)
          or 'clean')
    sys.exit(1 if f else 0)
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dir', required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--title', required=True)
    ap.add_argument('--description', required=True)
    ap.add_argument('--versions', default='19.0,20.0')
    ap.add_argument('--author', default='Independent (migration_knowledge_forge)')
    ap.add_argument('--tags', default='migration, upgrade')
    args = ap.parse_args()

    root = Path(args.dir)
    (root / 'references').mkdir(parents=True, exist_ok=True)
    (root / 'scripts').mkdir(parents=True, exist_ok=True)
    old, new = [v.strip() for v in args.versions.split(',')]
    (root / 'SKILL.md').write_text(SKILL_TMPL.format(
        name=args.name, description=args.description, author=args.author,
        versions_q=args.versions, tags=args.tags, title=args.title, old=old, new=new))
    (root / 'README.md').write_text(README_TMPL.format(title=args.title, name=args.name))
    (root / 'references' / '01-mapping.md').write_text(REF_TMPL.format(old=old, new=new))
    (root / 'scripts' / 'scanner.py').write_text(SCANNER_TMPL)
    here = Path(__file__).parent
    for s in ('check_markdown.py', 'normalize_markdown.py'):
        shutil.copy(here / s, root / 'scripts' / s)
    import importlib.util
    spec = importlib.util.spec_from_file_location('nm', here / 'normalize_markdown.py')
    nm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nm)
    for f in [root / 'SKILL.md', root / 'README.md', root / 'references' / '01-mapping.md']:
        f.write_text(nm.normalize(f.read_text()))
    print('scaffolded', root)
    print('next: fill references/01-mapping.md from branch_diff.py output; add PATTERNS to scanner.py;')
    print('      run check_markdown.py over all md; wire the skill into your plugin manifest.')


if __name__ == '__main__':
    main()
