# Pipeline B — mine verified deltas between two refs

## Research source ranking (S1–S6)

Rank evidence for *what changed* before trusting it. The completion tiers above govern
*how to fill a missing value*; this ranking governs *which source settles a claim*.

| Level | Source | Use |
|---|---|---|
| S1 | `git diff` of `Y.0` vs `X.0` in `odoo/odoo` | final arbiter for field/method/model/xml-id |
| S2 | Official Changelog (e.g. `.../orm/changelog.html`) | PR# + introducing version (which version a change belongs to) |
| S3 | `upgrade_code/` script inventory (`{ver}-{seq}-{name}.py`) | which changes already have a codemod; prefix = version |
| S4 | Companion cookbook (if any) | condensed readable source; re-verify against S1–S3 |
| S5 | Community upgrade posts (Cybrosys / SDLC / LineScripts / DeployMonkey …) | cross-check; **single community source ≠ conclusion** → tag `[verify]` |
| S6 | Enterprise `Y.0` tree | only for `[EE-verify]` rows |

Iron rule: any item from S5 not confirmed by S1–S3 is tagged `[verify]`; EE-only items
tagged `[EE-verify]`. Never invent an xml-id/method name — if it cannot be located, flag
it; never silently "complete" it.

## Fetch & diff

```bash
python3 scripts/branch_diff.py --repo odoo/odoo --a 19.0 --b 20.0 \
    --pairs "odoo/orm/models.py:odoo/orm/models.py,odoo/tools/__init__.py:odoo/tools/__init__.py" \
    --kind defs          # or: classes | exports | grep --pattern XYZ
```

- `defs`/`classes`: name-set diffs → candidate removals/additions.
- `exports`: ast-based re-export diff of `__init__` files (public surface changes).
- `grep`: occurrence counts + first matches (keyword retirement, e.g. `group_operator`).
- Path-level 404s are themselves findings (module moved/removed, e.g. `odoo/osv`).

## Confirm every candidate (no false rows)

1. Locate the successor: grep the new tree for the concept (`_has_cycle`, `aggregator`, …);
   read the signature/docstring, quote the file in the book/skill row.
2. Distinguish *removed* from *moved*: a name missing from one module often reappears
   in a sibling (check the package listing via the GitHub contents API).
3. Deprecated-but-present in the old ref (DeprecationWarning) is a **warning row**,
   absent-in-new is a **breaking row** — say which.
4. Vendor/private trees: row stays **[EE-verify]**; never auto-complete.
5. Record branch + file + date in the provenance appendix.

## Useful non-obvious mines

- `release.py` / setup: language & DB floors (e.g. `MIN_PY_VERSION`).
- CLI directory listing: new commands (`upgrade_code`).
- Codemod directory (`upgrade_code/`): the vendor's own migration intent; script
  names give version-stamped renames — mirror them in the checklist chapter.
- View/validation files: accepted tags/attrs (RNG), renamed view types.
- Tests module: removed helpers + new mock/context APIs (high value, low noise).

## From diffs to artifacts

- Book rows: `Book.table(['Old','New'], [[ [C(old)], [C(new), T(note)] ], …])`.
- Skill rows: reference md table with a provenance column (`src`/`doc`/`rec`/`EE`).
- Scanner: each breaking row whose old form is greppable becomes a PATTERNS entry
  (`auto` when a bundled codemod fixes it, else `manual`).
