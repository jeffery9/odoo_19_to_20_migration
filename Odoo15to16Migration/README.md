# Odoo15to16Migration

This is the **15→16** member of the multi-version migration workspace
(see the root README.md). The 16→17 member lives in
`../Odoo16to17Migration/` and the 17→18 member in `../Odoo17to18Migration/`.

## What this skill is

A machine-callable agent skill that migrates custom Odoo **15.0** addons to
**16.0** (CE and EE), using verified manual mappings. It is the companion to the
human-readable cookbook `../Odoo_Migration_Cookbook_15_to_16.md`.

15→16 is a **"data-model rename + payment/coupon restructure"** dominant migration:
the headline breaks are `payment.acquirer`→`payment.provider`, `coupon`→`loyalty`,
`ir_translation` removed (→JSONB), and a batch of model/module renames
(`stock.lot`, `account_analytic.plan`, `mail.channel.member`, `account.report`, …).
Unlike 16→17 (views) and 17→18 (removals), 15→16 has **no `upgrade_code` codemod**
and the view syntax is almost unchanged.

## Contents

- `SKILL.md` — frontmatter, workflow, and red lines for the 15→16 jump.
- `references/` — condensed, source-verified mapping tables:
  - `payment-loyalty.md` — payment.acquirer→provider + coupon→loyalty renames.
  - `models-mapping.md` — other model/module renames + ir_translation→JSONB.
  - `orm-api.md` — track_visibility→tracking, api.multi removal, website routing.
  - `views-qweb.md` — what is unchanged in 16 (attrs/states/tree valid) + [verify] t-raw/html sanitize.
  - `security.md` — res.groups / ir.model.access.csv unchanged in 15→16.
  - `upgrade-code.md` — 16.0 has zero codemods; use OpenUpgrade for DB renames.
- `scripts/` — `scan_addon.py` (detects 15-only APIs), `check_markdown.py`,
  `normalize_markdown.py` (stdlib-only QA).

## Usage

```bash
python3 scripts/scan_addon.py /path/to/addons            # triage (exit 1 = findings)
python3 scripts/scan_addon.py /path/to/addons --json     # machine-readable
python3 scripts/scan_addon.py /path/to/addons --addon my_module
```

Then apply the manual mappings from `references/*.md`, write data migrations in
each module's `migrations/16.0/`, re-scan (expect 0), and run
`odoo-bin -u <module> --test-tags /<module>` on a 16.0 sandbox.

## Scope guard

This skill is for **15.0 → 16.0 only**. Do NOT perform 16→17 work here
(attrs/states rejection, tree still valid, get_resource_path→file_path, hooks env
arg) — that belongs to `../Odoo16to17Migration/`. See `SKILL.md` "Hard rules".
