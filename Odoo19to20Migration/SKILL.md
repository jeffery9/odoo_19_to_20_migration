---
name: odoo_19_to_20_migration
description: Migrates custom Odoo 19.0 addons to 20.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 19 to 20, fix 20.0 deprecations (ir.access.csv, models.Constraint, check_access/has_access, _has_cycle, read_group signature, aggregator, Domain.custom, owl3 t-call order, route jsonrpc, ormcache), run or extend odoo-bin upgrade_code codemods, or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 19-only APIs.
version: 20.0.1
author: Independent (companion to the Odoo Migration Cookbook I & II)
category: migration
odoo_versions: ["19.0", "20.0"]
tags: [odoo, migration, upgrade, orm, security, views, qweb, owl, testing, codemod, upgrade_code]
---

# Odoo 19 → 20 Migration

## Goal

Take a 19.0 custom addon (or a whole addons tree) to 20.0 with no leftover
19-only API, using automated codemods first and verified manual mappings second.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables from the
  companion cookbooks (Volume I fixed edition + Volume II "Closing the Gaps").
- Upstream trees: github.com/odoo/odoo branches `19.0` and `20.0`.
- Bundled codemods: `odoo/upgrade_code/` + `odoo-bin upgrade_code` (see
  `references/upgrade-code.md`).
- Items tagged **[EE-verify]** are Enterprise-only: they MUST be re-checked
  against the matching Enterprise 20.0 tree before deployment; never present
  them as verified.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 20.0 replacement, and whether a bundled codemod fixes it.
2. **Codemod first** — on a clean git branch:
   `odoo-bin upgrade_code --from 19.0 --addons-path /path/to/addons --dry-run`,
   then the real run; review `git diff` file by file and commit.
   Codemods rewrite SOURCE only; data upgrades stay in module migrations.
3. **Manual mappings** — for everything the scanner flags as `manual`, apply
   the replacement from the matching reference file:
   - security file & ORM renames → `references/security-and-orm.md`
   - binary/excel/pdf/time, HTTP routes, mail/server actions → `references/binary-http-mail.md`
   - view xpaths, ribbons/icons, kanban cards, QWeb & Owl 3 → `references/views-qweb-owl.md`
   - model/field/xml-id maps per business module → `references/modules-mapping.md`
   - runtime/imports, cache & SQL, model-API deltas, fields/domains, tests → `references/api-deltas-vol2.md`
   - codemod usage & how to write your own scripts → `references/upgrade-code.md`
4. **Validate** — re-run the scanner (expect 0 findings), then:
   `odoo-bin -u <module> --test-tags /<module>` in a 20.0 sandbox; fix view
   validation errors (RNG) and domain `TypeError`s last, they are the loudest.
5. **Report** — summarize per addon: codemod changes, manual edits (with the
   reference anchor used), remaining [EE-verify] items, test status.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 20.0 tree (or the
  mapping tables, which cite their source file). Unverifiable EE ids stay
  flagged, never silently "completed".
- `ir.model.access.csv` and `perm_*` columns are illegal in 20: the file is
  `security/ir.access.csv` with `operation` strings (`cru`, `c`, …) and rule
  domains merged in; `[(1,'=',1)]`-style domains must become empty.
- Never keep `type='json'` routes for web-client calls; external integrations
  keep using JSON-2 `/json/2/<model>/<method>` (still present in 20).
- Long xpaths/code in tables wrap instead of truncating: when you copy a value
  from a clipped source, verify it against the tree before committing.
