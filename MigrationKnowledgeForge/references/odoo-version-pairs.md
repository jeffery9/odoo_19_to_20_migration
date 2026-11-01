# Odoo version-pair profiles (any-pair support)

The forge is pair-parameterized: every pipeline takes the old/new refs explicitly.
This file holds the **verified structural matrix** and ready-made presets so a
new pair (17→18, 18→19, 19→20, …) can be instantiated without re-discovery.
All rows verified against `odoo/odoo` branch listings / `release.py` / `setup.py` /
`ir_ui_view.py` on 2026-10-11.

## Structural matrix per branch

| Branch | `odoo/models` | `odoo/orm` pkg | `odoo/osv` | `odoo/http` | `odoo/upgrade_code` | view type | Python floor |
|---|---|---|---|---|---|---|---|
| 17.0 | single `models.py` | — | present | `http.py` | — | `tree` | ≥3.10 |
| 18.0 | single `models.py` | — | present | `http.py` | present (`17.5-*`) | `list` | ≥3.10 |
| 19.0 | shim package | present | present | `http.py` | present (`17.5–18.5-*`) | `list` | ≥3.10 |
| 20.0 | shim package | present (+`cache`,`models_cached`,`query`) | **removed** | package | present (`17.5–20.0-*`) | `list` | ≥3.12 |

Consequences (verified):

- The `tree`→`list` view rename lands in **18** (codemod `17.5-01-tree-to-list` ships in the 18 tree).
- The ORM package split + shim packages land in **19**; `odoo/osv` survives until **20**.
- The Python floor jump (3.10→3.12) happens only at **20**.
- Codemod rule: **run `upgrade_code` from the TARGET branch** — a release ships the
  scripts for the span that ends in it (18 tree: `17.5-*`; 19 tree: `+18.x`; 20 tree: `+19.x/20.0`).
  Targets without `upgrade_code` (≤17) ⇒ manual mappings only.

## Hand-only era (≤17) vs codemod era (18→20)

The matrix above concentrates on the codemod era because that is where `upgrade_code`
exists. For the **hand-only era (5 → 17)** the forge has produced 13 version pairs with
**no codemod**: every break is a manual mapping row backed by an OpenUpgrade script or a
hand-written `references/` entry. Discipline for these:

- **All scanner PATTERNS are `manual`** — there is no `auto` (no bundled codemod to mirror).
  The scanner's job is pure triage: flag the old form so a human applies the mapping.
- **OpenUpgrade is the de-facto engine** for CE upgrades in this era; cite its module
  (`openupgrade-scripts`) as the `src` provenance where applicable.
- The canonical change-ownership for this era *and* the codemod era is consolidated in
  `version-scope-redlines.md` — consult it **before**
  forging any pair to avoid mis-attributing a break to the wrong X→Y.
- Presets / path-shifts above target the codemod era; for ≤17 point
  `scripts/diff_core_models.py --repo <local-odoo> --ref-a <x> --ref-b <y> --model <m>`
  (local git, auto-locates module dirs) at the real tree, or mine OCA / OpenUpgrade
  commit history for the deltas.

## Version-scope discipline

A change enters the X→Y artifact only if it **first appears at ≥ X.0 and ≤ Y.0**.

- Read the Online/minor number in the Changelog (e.g. 17.2, 18.1, 18.5, 19.1, 19.3, 19.4);
  that minor is where the change lands.
- If a change's introducing version is **< X.0** (X already contains it), do **not** list
  it in X→Y — mention it only in a footnote about cleaning up legacy X code.
- Codemod script prefixes encode the version (`18.1-00-sql-constraint`). A script fires in
  an X→Y run only when its version ∈ [X.0, Y.0] (see the codemod-target rule above); e.g.
  `19.1/19.3/19.4` scripts do **not** run in a pure 18→19 CE upgrade (they belong to 19.x
  Online / 20).

Counter-examples that look like 18→19 but are **not** (do not drag them in):
`ir.access.csv` conversion (19.4 → belongs to 19→20); model-level `models.Constraint` as a
*requirement* (optional since 18.1); `check_access`/`has_access` (18.0); `Domain` API (18.1);
`aggregator` rename (17.2); `tree`→`list` (17.5, codemod ships in the 18 tree). These are
either earlier or already present in 18 — including them would violate version scope.

## Pair presets for `branch_diff.py`

17→18:
`--pairs "odoo/addons/base/models/ir_ui_view.py,odoo/tools/__init__.py,setup.py"`
18→19 (path-shifting pairs):
`--pairs "odoo/models.py:odoo/orm/models.py,odoo/fields.py:odoo/orm/fields.py,odoo/api.py:odoo/orm/decorators.py,odoo/tools/__init__.py,odoo/osv/expression.py:odoo/orm/domains.py"`
19→20:
`--pairs "odoo/orm/models.py,odoo/orm/fields.py,odoo/tools/__init__.py,odoo/osv/expression.py:odoo/orm/domains.py,odoo/tests/common.py,odoo/release.py"`
(Use `--kind defs|exports|classes|grep`; a 404 side is itself a finding.)

## Landmark deltas to seed scanners/books (verified, extend per pair)

- 17→18: view type/tag `tree`→`list` (codemod in 18 tree); no Python floor change.
- 18→19: ORM moves to `odoo/orm` with shim packages (imports `from odoo import models,
  fields, api` keep working); codemod series `18.1-00-sql-constraint`,
  `18.1-02-route-jsonrpc`, `18.2/18.3/18.5-*` available in the 19 tree.
- 19→20: `odoo/osv` removed; `Domain`/`Query`/cache moves (see Vol-II tables);
  `read_group` signature overhaul; Python ≥3.12; codemod series `19.x/20.0` in 20 tree.

## Instantiating a new pair (procedure)

1. Refs: old=`X.0`, new=`Y.0` (or `saas-*`/`master` when relevant).
2. Run the preset (or build one from the matrix: pair old-path:new-path where modules moved).
3. Confirm candidates per `source-diff-mining.md` (successor grep, deprecated-vs-removed,
   EE/private flags) → delta tables with provenance column.
4. `skill_scaffold.py --versions "X.0,Y.0"`; seed `scanner.py` PATTERNS from breaking rows
   (`auto` only when the TARGET branch ships a codemod for it; **all `manual` for ≤17**).
5. Optional cookbook: `booklib.py` (version-agnostic); cover/edition strings carry the pair.
6. QA: `check_markdown.py` 0 issues; `verify_pdf.py` 0 overflow; scanner clean-addon exit 0;
   run the pair's `check_cookbook_consistency.py` (Cookbook ↔ `references/` zero drift).
7. If this is the 2nd+ pair, update the cross-version index (pipeline G):
   add the pair's business-model changes to `Core_Models_Changelog.md` (event table +
   per-pair summary), respecting `version-scope-redlines.md`.
