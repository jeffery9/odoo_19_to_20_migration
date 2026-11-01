#!/usr/bin/env python3
"""Diff Odoo core business models between two version refs (pipeline G tool).

A model/field-level companion to MigrationKnowledgeForge/scripts/branch_diff.py.
Two data sources:

  1. LOCAL GIT (preferred) — point --repo at a checked-out odoo/odoo or
     odoo-enterprise tree and pass --ref-a / --ref-b (branch/tag/sha).
     Works offline, reads real source via `git show ref:path`.

  2. NETWORK (fallback) — without --repo, fetches raw .py from GitHub
     (or --base-url mirror) using the old --pairs path syntax.

Modes
  --scan-modules "account,sale,stock"   model-set diff (added/removed _name)
  --model account.move                 field-level diff for ONE model
  --scan-modules "..." --focus-models "account.move,stock.picking"
                                         model-set diff + field diff for focus list

Module directories are located by searching for `<module>/__manifest__.py` (or
`__openerp__.py`) inside the ref, so it adapts to any layout
(`addons/<m>`, `odoo/addons/<m>`, enterprise root `<m>`, ...).

Usage
  # local: which account models appeared/disappeared 12.0 -> 13.0
  python3 diff_core_models.py --repo /Volumes/ssd-1tb/_repos/odoo \\
      --ref-a 12.0 --ref-b 13.0 --scan-modules account

  # local: field changes of stock.picking 13.0 -> 14.0
  python3 diff_core_models.py --repo /Volumes/ssd-1tb/_repos/odoo \\
      --ref-a 13.0 --ref-b 14.0 --model stock.picking

  # EE-only model
  python3 diff_core_models.py --repo /Volumes/ssd-1tb/_repos/odoo-enterprise \\
      --ref-a 19.0 --ref-b 20.0 --model hr.payslip.input.type

  python3 diff_core_models.py --self-test     # offline AST sanity check
"""
import argparse
import ast
import re
import subprocess
import sys
import urllib.request
import warnings

warnings.filterwarnings('ignore', category=SyntaxWarning)  # Odoo source has \s/\d escapes in literals

DEFAULT_BASE = 'https://raw.githubusercontent.com/{repo}/{ref}/{path}'


# ---------------------------------------------------------------------------
# git helpers (subprocess list-calls => no shell quoting issues)
# ---------------------------------------------------------------------------
def git(repo, *args, capture=True, check=True):
    cmd = ['git', '-C', repo] + list(args)
    res = subprocess.run(cmd, capture_output=capture, text=True)
    if check and res.returncode != 0:
        raise RuntimeError('git %s failed: %s' % (' '.join(args), res.stderr.strip()))
    return res.stdout if capture else None


def resolve_ref(repo, ref):
    """Return a usable ref; try `ref` then `origin/ref`."""
    try:
        git(repo, 'rev-parse', '--quiet', '--verify', '%s^{commit}' % ref)
        return ref
    except RuntimeError:
        try:
            git(repo, 'rev-parse', '--quiet', '--verify', 'origin/%s^{commit}' % ref)
            return 'origin/%s' % ref
        except RuntimeError:
            return None


def list_files(repo, ref):
    out = git(repo, 'ls-tree', '-r', '--name-only', ref, check=False)
    return [l for l in out.splitlines() if l.endswith('.py')]


def show_file(repo, ref, path):
    res = subprocess.run(['git', '-C', repo, 'show', '%s:%s' % (ref, path)],
                        capture_output=True, text=True)
    if res.returncode != 0:
        return None
    return res.stdout


def find_module_dir(repo, ref, module, files):
    for f in files:
        if f.endswith('__manifest__.py') or f.endswith('__openerp__.py'):
            d = f.rsplit('/', 1)[0]
            if d == module or d.endswith('/' + module):
                return d
    return None


# ---------------------------------------------------------------------------
# extraction
# ---------------------------------------------------------------------------
def _const_list(node):
    if isinstance(node, ast.Constant):
        return [node.value]
    if isinstance(node, (ast.List, ast.Tuple)):
        return [e.value for e in node.elts if isinstance(e, ast.Constant)]
    if isinstance(node, ast.Dict):
        return [k.value for k in node.keys if isinstance(k, ast.Constant)]
    return []


def _field_type(call):
    f = call.func
    if not isinstance(f, ast.Attribute):
        return None
    val = f.value
    name = val.id if isinstance(val, ast.Name) else (val.attr if isinstance(val, ast.Attribute) else None)
    return f.attr if name == 'fields' else None


def extract(src):
    """List of {name, inherit, fields:{f:type}, cls} for class-level models."""
    models = []
    if not src:
        return models
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return _extract_regex(src)
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        info = {'name': None, 'inherit': [], 'fields': {}, 'cls': node.name}
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for tgt in stmt.targets:
                    if isinstance(tgt, ast.Name):
                        if tgt.id == '_name' and isinstance(stmt.value, ast.Constant):
                            info['name'] = stmt.value.value
                        elif tgt.id == '_inherit':
                            info['inherit'] = _const_list(stmt.value)
                        elif isinstance(stmt.value, ast.Call):
                            ft = _field_type(stmt.value)
                            if ft:
                                info['fields'][tgt.id] = ft
            elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                if isinstance(stmt.value, ast.Call):
                    ft = _field_type(stmt.value)
                    if ft:
                        info['fields'][stmt.target.id] = ft
        if info['name'] or info['fields']:
            models.append(info)
    return models


_RE_NAME = re.compile(r"^\s*_name\s*=\s*['\"]([^'\"]+)['\"]", re.M)
_RE_FIELD = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*fields\.([A-Za-z]+)\(", re.M)


def _extract_regex(src):
    """Fallback for old py2 syntax that breaks ast.parse (e.g. `except X, e:`)."""
    models = []
    current = None
    for line in src.splitlines():
        m = _RE_NAME.search(line)
        if m:
            current = {'name': m.group(1), 'inherit': [], 'fields': {}, 'cls': '?'}
            models.append(current)
            continue
        f = _RE_FIELD.search(line)
        if f and current is not None:
            current['fields'][f.group(1)] = f.group(2)
    return models


def effective_name(info):
    """Primary model name: _name, else first _inherit entry."""
    if info['name']:
        return info['name']
    if info['inherit']:
        return info['inherit'][0]
    return None


def aggregate(models):
    """Map model name -> set of field types (union across files/extensions)."""
    agg = {}
    for m in models:
        en = effective_name(m)
        if not en:
            continue
        agg.setdefault(en, {}).update(m['fields'])
    return agg


# ---------------------------------------------------------------------------
# report helpers
# ---------------------------------------------------------------------------
def report_model_set(ra, rb, refa, refb, modules):
    print('## Model inventory diff: `%s` → `%s`' % (refa, refb))
    print('modules: %s\n' % ', '.join('`%s`' % m for m in modules))
    for mod in modules:
        fa = list_files(ra, refa)
        fb = list_files(rb, refb)
        da = find_module_dir(ra, refa, mod, fa)
        db = find_module_dir(rb, refb, mod, fb)
        if not da or not db:
            print('- `%s`: dir not found (a=%s b=%s) — skip' % (mod, da, db))
            continue
        names_a = _module_names(ra, refa, da)
        names_b = _module_names(rb, refb, db)
        removed = sorted(names_a - names_b)
        added = sorted(names_b - names_a)
        kept = len(names_a & names_b)
        print('- **%s** (a=%s, b=%s)' % (mod, da, db))
        print('  - models kept: %d' % kept)
        if added:
            print('  - added  : %s' % ', '.join('`%s`' % x for x in added))
        if removed:
            print('  - removed: %s' % ', '.join('`%s`' % x for x in removed))
        for r in removed:
            for a in added:
                if r.split('.')[-1] == a.split('.')[-1]:
                    print('    ↳ possible rename: `%s` → `%s`' % (r, a))
        print()


def _module_names(repo, ref, moddir):
    files = [f for f in list_files(repo, ref) if f.startswith(moddir + '/')]
    names = set()
    for f in files:
        src = show_file(repo, ref, f)
        for m in extract(src):
            if m['name']:
                names.add(m['name'])
    return names


def report_field_diff(repo_a, repo_b, refa, refb, models):
    print('## Field diff: `%s` → `%s`\n' % (refa, refb))
    for model in models:
        agg_a = _model_fields(repo_a, refa, model)
        agg_b = _model_fields(repo_b, refb, model)
        if agg_a is None and agg_b is None:
            print('- `%s`: not found in either ref' % model)
            continue
        fa = agg_a or {}
        fb = agg_b or {}
        removed = sorted(set(fa) - set(fb))
        added = sorted(set(fb) - set(fa))
        changed = sorted(n for n in (set(fa) & set(fb)) if fa[n] != fb[n])
        print('- **`%s`** (found a=%s b=%s)' % (model, agg_a is not None, agg_b is not None))
        if added:
            print('  - fields added   : %s' % ', '.join('`%s`(%s)' % (n, fb[n]) for n in added))
        if removed:
            print('  - fields removed : %s' % ', '.join('`%s`(%s)' % (n, fa[n]) for n in removed))
        if changed:
            print('  - type changed   : %s' % ', '.join('`%s` %s→%s' % (n, fa[n], fb[n]) for n in changed))
        if not (added or removed or changed):
            print('  - (no field-level change detected)')
        print()


def _model_fields(repo, ref, model):
    """Union of fields for `model` across every file that defines/inherits it."""
    if resolve_ref(repo, ref) is None:
        return None
    # find files that mention the model's _name (both quote styles)
    pats = ["_name = '%s'" % model, '_name = "%s"' % model,
            "_inherit = '%s'" % model, '_inherit = "%s"' % model]
    try:
        out = git(repo, 'grep', '-l', '-e', pats[0], '-e', pats[1], '-e', pats[2], '-e', pats[3],
                  ref, '--', '*.py', check=False)
    except RuntimeError:
        out = ''
    files = [l.split(':', 1)[1] if ':' in l else l for l in out.splitlines() if l.strip()]
    if not files:
        return None
    union = {}
    for f in sorted(set(files)):
        src = show_file(repo, ref, f)
        for m in extract(src):
            en = effective_name(m)
            if en == model:
                union.update(m['fields'])
    return union or None


# ---------------------------------------------------------------------------
# network fallback (original behaviour)
# ---------------------------------------------------------------------------
def fetch(base_url, repo, ref, path, timeout=20):
    url = base_url.format(repo=repo, ref=ref, path=path)
    try:
        return urllib.request.urlopen(url, timeout=timeout).read().decode()
    except Exception:
        return None


def self_test():
    sample_old = '''
from odoo import models, fields
class AccountInvoice(models.Model):
    _name = 'account.invoice'
    number = fields.Char()
    amount = fields.Monetary()
class ResPartner(models.Model):
    _name = 'res.partner'
    customer = fields.Boolean()
'''
    sample_new = '''
from odoo import models, fields
class AccountMove(models.Model):
    _name = 'account.move'
    name = fields.Char()
    amount_total = fields.Monetary()
class ResPartner(models.Model):
    _name = 'res.partner'
    customer_rank = fields.Integer()
'''
    print('## self-test (offline AST)')
    a_by, b_by = aggregate(extract(sample_old)), aggregate(extract(sample_new))
    removed = sorted(set(a_by) - set(b_by))
    added = sorted(set(b_by) - set(a_by))
    name = sorted(set(a_by) & set(b_by))[0]
    f_removed = sorted(set(a_by[name]) - set(b_by[name]))
    f_added = sorted(set(b_by[name]) - set(a_by[name]))
    print('   model names removed:', removed)
    print('   model names added  :', added)
    print('   common model       :', name)
    print('   fields removed     :', f_removed)
    print('   fields added       :', f_added)
    print('   OK' if (removed and added and f_removed and f_added) else '   UNEXPECTED')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repo', help='local git repo path (enables local mode)')
    ap.add_argument('--ref-a', help='old git ref (e.g. 12.0 / origin/7.0)')
    ap.add_argument('--ref-b', help='new git ref (e.g. 13.0)')
    ap.add_argument('--scan-modules', help='comma list of module names for model-set diff')
    ap.add_argument('--model', help='single model name for field diff')
    ap.add_argument('--focus-models', help='comma list; field-diff these within --scan-modules')
    ap.add_argument('--pairs', help='NETWORK mode: old_path:new_path[,...]')
    ap.add_argument('--kind', choices=['models', 'fields', 'all'], default='all')
    ap.add_argument('--repo-net', default='odoo/odoo', help='network repo (default odoo/odoo)')
    ap.add_argument('--base-url', default=DEFAULT_BASE, help='raw file URL template')
    ap.add_argument('--self-test', action='store_true', help='offline AST sanity check')
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    # --- local git mode ---
    if args.repo:
        if not (args.ref_a and args.ref_b):
            ap.error('local mode needs --ref-a and --ref-b')
        ra, rb = args.repo, args.repo
        refa, refb = resolve_ref(ra, args.ref_a), resolve_ref(rb, args.ref_b)
        if not refa or not refb:
            ap.error('could not resolve refs (a=%s b=%s). Try origin/<x>.' % (refa, refb))
        if args.scan_modules:
            mods = [m.strip() for m in args.scan_modules.split(',') if m.strip()]
            report_model_set(ra, rb, refa, refb, mods)
            if args.focus_models:
                fms = [m.strip() for m in args.focus_models.split(',') if m.strip()]
                report_field_diff(ra, rb, refa, refb, fms)
            return
        if args.model:
            report_field_diff(ra, rb, refa, refb, [args.model])
            return
        ap.error('local mode needs --scan-modules or --model')

    # --- network fallback ---
    if args.pairs:
        if not (args.ref_a and args.ref_b):
            ap.error('network mode needs --ref-a/--ref-b (aliased to --a/--b)')
        for pair in args.pairs.split(','):
            pa, pb = (pair.split(':') + [pair.split(':')[0]])[:2] if ':' in pair else (pair, pair)
            a_src = fetch(args.base_url, args.repo_net, args.ref_a, pa)
            b_src = fetch(args.base_url, args.repo_net, args.ref_b, pb)
            _report_pair(pa, pb, a_src, b_src, args.kind, args.ref_a, args.ref_b)
        return
    ap.error('nothing to do: pass --repo+--ref-a/--ref-b+--scan-modules/--model, '
             'or --pairs (network), or --self-test')


def _report_pair(pa, pb, a_src, b_src, kind, refa, refb):
    a_models = extract(a_src)
    b_models = extract(b_src)
    print('## %s (%s) → %s (%s)' % (pa, refa, pb, refb))
    if a_src is None or b_src is None:
        print('   file-level delta: present a=%s b=%s' % (a_src is not None, b_src is not None))
        return
    a_by, b_by = aggregate(a_models), aggregate(b_models)
    a_names, b_names = set(a_by), set(b_by)
    if kind in ('models', 'all'):
        removed = sorted(a_names - b_names)
        added = sorted(b_names - a_names)
        print('   model names removed (%d): %s' % (len(removed), ', '.join('`%s`' % x for x in removed) or '—'))
        print('   model names added   (%d): %s' % (len(added), ', '.join('`%s`' % x for x in added) or '—'))
        if len(removed) == 1 and len(added) == 1:
            print('   ↳ likely rename: `%s` → `%s`' % (removed[0], added[0]))
    if kind in ('fields', 'all'):
        for name in sorted(a_names & b_names):
            fa, fb = a_by[name], b_by[name]
            rem = sorted(set(fa) - set(fb))
            add = sorted(set(fb) - set(fa))
            chg = sorted(n for n in (set(fa) & set(fb)) if fa[n] != fb[n])
            if not (rem or add or chg):
                continue
            print('   ### model `%s`' % name)
            if rem:
                print('      fields removed (%d): %s' % (len(rem), ', '.join('`%s`(%s)' % (n, fa[n]) for n in rem)))
            if add:
                print('      fields added   (%d): %s' % (len(add), ', '.join('`%s`(%s)' % (n, fb[n]) for n in add)))
            if chg:
                print('      fields type-changed (%d): %s' % (len(chg), ', '.join('`%s` %s→%s' % (n, fa[n], fb[n]) for n in chg)))


if __name__ == '__main__':
    main()
