# Pipeline G — cross-version core-model changelog (index, not source of truth)

When the forge has produced **≥ 2 version pairs**, a cross-cutting deliverable becomes
valuable: a single **`Core_Models_Changelog.md`** that tracks *Odoo standard core
business models* (`account.move`, `sale.order`, `purchase.order`, `stock.picking`,
`res.partner`, `product.product`, `hr.employee`, …) across **every** version pair
(5.0 → 20.0). It is an **index** — it reuses facts already verified in each pair's
cookbook / `references/` and never invents new claims.

A worked instance lives at the workspace root: `Core_Models_Changelog.md`, produced
alongside `scripts/diff_core_models.py` (the model/field-level diff tool adopted into
this meta-skill).

## When to produce

- After the second version pair is forged, or on explicit request ("track core model
  changes across versions").
- Produced **once**, then maintained incrementally as new pairs are added (see SOP).
- It is **not** part of the per-pair two-artifact contract (Cookbook + Skill); it is a
  cross-cutting layer that sits *above* all pairs and points into them.

## Anatomy of `Core_Models_Changelog.md`

1. **Legend + version-scope red lines** — state the first-appears discipline and link
   to `version-scope-redlines.md`. This is what keeps the index honest.
2. **Core model change-event table** — one row per (model, change, version-pair), with
   columns `model`, `change type` ∈ {rename, field-added, field-removed, field-renamed,
   deprecated, behaviour}, `version pair`, `confidence` ∈ {CONFIRMED, `[verify]`,
   `[EE-verify]`}, `automation` ∈ {`codemod:<name>`, `OpenUpgrade`, manual}, and `source`
   (the pair cookbook / `references/` file that proves it).

3. **Per-pair summary** — for each X→Y, a one-paragraph "what happened at the business
   model layer", so a reader sees the whole arc 5→20 at a glance.
4. **Red-line exclusions** — explicit "these look like breaks but are owned elsewhere"
   table (mirrors `version-scope-redlines.md`).
5. **Tooling + maintenance SOP** — how to recompute via `diff_core_models.py` and how
   to promote `[verify]` → `CONFIRMED`.

## The diff tool — `scripts/diff_core_models.py`

A model/field-specialised cousin of `branch_diff.py`. **Primary mode: local git** — point
`--repo` at a checked-out `odoo` / `odoo-enterprise` tree and diff two refs by reading real
source via `git show <ref>:<path>` (no network). It AST-extracts `_name` / `_inherit` /
`fields.X`, aggregates a model's fields across every file that defines or inherits it, and
emits a Markdown-ready delta.

```bash
# offline self-check (no repo, no network)
python3 scripts/diff_core_models.py --self-test

# model inventory diff of a module between two refs
python3 scripts/diff_core_models.py --repo /path/to/odoo \
  --ref-a 12.0 --ref-b 13.0 --scan-modules account

# field-level diff of one model (auto-locates defining/inheriting files)
python3 scripts/diff_core_models.py --repo /path/to/odoo \
  --ref-a 13.0 --ref-b 14.0 --model stock.picking

# model-set diff + field diff for a focus list
python3 scripts/diff_core_models.py --repo /path/to/odoo \
  --ref-a 19.0 --ref-b 20.0 --scan-modules account,sale,stock --focus-models account.move

# EE-only model
python3 scripts/diff_core_models.py --repo /path/to/odoo-enterprise \
  --ref-a 19.0 --ref-b 20.0 --model hr.payslip.input.type
```

Notes:

- Module directories are located by searching for `<module>/__manifest__.py` (or
  `__openerp__.py`) inside the ref, so it adapts to `addons/<m>`, `odoo/addons/<m>`, and
  enterprise-root `<m>` layouts without hard-coded paths.
- Refs may be bare branches (`12.0`) or remote-only (`origin/7.0`); an absent ref is retried
  as `origin/<ref>`.
- Old py2 syntax (`except X, e:`) breaks `ast.parse`, so extraction falls back to a regex
  reader that still recovers `_name` and simple `x = fields.X(...)` declarations.
- Network fallback: omit `--repo` and use `--ref-a/--ref-b --pairs "old:new"` (GitHub raw or
  `--base-url` mirror); a fetch failure degrades to a file-level delta rather than crashing.
- `--self-test` proves the AST logic offline (rename + field add/remove both detected).

## Maintenance SOP (promote `[verify]` → `CONFIRMED`)

1. Pick a `[verify]` row whose *source* is a model field/model rename.
2. Run `diff_core_models.py --repo <local> --ref-a <X>.0 --ref-b <Y>.0 --model <model>` (or `--scan-modules <m>` for a model-set diff).
3. If the tool's output matches the row, change confidence to `CONFIRMED` in **both**
   the changelog and the owning pair's cookbook / `references/` (consistency rule).
4. If it contradicts, flag and re-open the owning pair's `VERIFY_TRACKER.md`.

## Relationship to per-pair artifacts

`Core_Models_Changelog.md` is the **index**; each `OdooXXtoYYMigration/references/`
remains the **source of truth** for that pair. The index MUST stay fact-aligned to the
pairs (same rule as Skill-vs-Cookbook): on conflict, the pair wins and the index is
patched back. Never add a model-change claim to the index that is not backed by a pair.
