---
name: odoo_17_to_18_migration
description: Migrates custom Odoo 17.0 addons to 18.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 17 to 18, fix 18.0 removals (name_get removed, check_access_rights/check_access_rule/user_has_groups/check_recursion removed, inselect operator removed, <tree> view type removed), apply renames (check_access/_filtered_access/has_access, _search_display_name, aggregator, type='json'→jsonrpc, tree→list), run or extend odoo-bin upgrade_code codemods (17.5-01-tree-to-list), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 17-only APIs.
version: 18.0.1
author: Independent (companion to the Odoo Migration Cookbook I & II)
category: migration
odoo_versions: ["17.0", "18.0"]
tags: [odoo, migration, upgrade, orm, views, qweb, security, api, codemod, upgrade_code]
---

# Odoo 17 → 18 Migration

## Goal

Take an 17.0 custom addon (or a whole addons tree) to 18.0 with no leftover
17-only API, using a single bundled codemod first (`tree`→`list`) and verified
manual mappings second.

> **Scope note.** This skill covers the **17.0 → 18.0** jump only (including 18.x
> Online minors that are new relative to 17). The 18→19 skill
> (`Odoo18to19Migration/`) handles the next step (Owl 3, ORM package split,
> `res.groups` privilege model, `web_editor` split, `ir.access.csv`). Many items
> already changed *before* 18 (e.g. `aggregator` rename in 17.2) are listed here
> only where they are still *relevant to cleaning up 17 code*, never as if they
> were new in 18.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  17→18 jump. Primary anchors:
  - Odoo ORM Changelog: `odoo.com/documentation/18.0/developer/reference/backend/orm/changelog.html`
    (PRs #122085, #127353, #137031, #144747, #151597, #154132, #159528, #159909,
    #170009, #171371, #174844, #174967, #179148, #183636).
  - GitHub `odoo/odoo` branch `18.0` source (verified `ir_ui_view.py` `type`
    selection = `list` only; `models.py` removes `name_get`/`_name_search`/
    `check_access_rights`/`user_has_groups`/`check_recursion`; `upgrade_code/`
    contains only `17.5-01-tree-to-list`).
  - OCA `maintainer-tools`《Migration to version 18.0》; Cybrosys《Odoo 18 v/s
    Odoo 17》; ODIWARE; DeployMonkey (cross-checked).
- Bundled codemods: `odoo/upgrade_code/` + `odoo-bin upgrade_code` (see
  `references/upgrade-code.md`).
- Items tagged **[EE-verify]** are Enterprise-only: they MUST be re-checked
  against the matching Enterprise 18.0 tree before deployment; never present
  them as verified. Items tagged **[verify]** are reported by community
  upgrade guides but not yet confirmed against the 18.0 source — confirm
  before relying on them.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 18.0 replacement, and whether a bundled codemod fixes it
   (only `tree`→`list` is auto).
2. **Codemod first** — on a clean git branch, from an **18.0** installation:
   `odoo-bin upgrade_code --from 17.0 --addons-path /path/to/addons --dry-run`,
   then the real run; review `git diff` file by file (eyeball the `tree`→`list`
   rewrite — `editable`/`create`/`default_order` can land outside the tag) and commit.
   Note: 17→18 ships **only one** codemod (`17.5-01-tree-to-list`); all other
   fixes are manual.
3. **Manual mappings** — for everything the scanner flags as `manual`, apply
   the replacement from the matching reference file:
   - views / QWeb / frontend → `references/views-qweb.md`
   - ORM & model API renames → `references/orm-api.md`
   - HTTP/RPC/mail/binary → `references/http-rpc-mail.md`
   - security file & `res.groups` (unchanged in 17→18) → `references/security.md`
   - module/model/field maps + symptom index → `references/modules-mapping.md`
   - codemod usage & how to write your own scripts → `references/upgrade-code.md`
4. **Validate** — re-run the scanner (expect 0 findings), then:
   `odoo-bin -u <module> --test-tags /<module>` in an 18.0 sandbox; fix view
   validation errors (RNG) and domain `TypeError`s last, they are the loudest.
   Also start the server with deprecation warnings enabled (`--dev=all` /
   log-level) and clear every `DeprecationWarning` — those are 18→19's hard-breaks.
5. **Report** — summarize per addon: codemod changes, manual edits (with the
   reference anchor used), remaining [EE-verify]/[verify] items, test status.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 18.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **The `tree`→`list` rename is the headline breaking change.** A leftover
  `<tree>` (in a view, a `view_mode`, or an inherited-view XPath `//tree`) throws
  `ValueError: Wrong value for ir.ui.view.type: 'tree'`. Run the codemod and then
  grep for any stragglers.
- **Security file & `res.groups` are UNCHANGED in 17→18.** Keep
  `security/ir.model.access.csv` with `perm_*` columns — do **not** apply the
  19→20 `ir.access.csv`/`operation` conversion here. `res.groups.category_id` /
  `groups_id` / `users` keep their 17 names.
- `web_editor` still exists in 18 — do **not** repoint its `depends` (that is
  18→19). Owl is still **Owl 2** in 18 — no `setup()` rewrite needed (that is 19.0).
- `name_get`, `_name_search`, `check_access_rights`, `check_access_rule`,
  `user_has_groups`, `check_recursion`, the `inselect` domain operator are
  **removed** in 18 — delete/replace them; they are not just deprecated.
- Python: Odoo 18 keeps the **Python 3.10+** floor (no jump vs 17); PostgreSQL
  **14+** recommended `[verify]`. Verify the runtime before migrating.
- When copying a value from a clipped/secondary source, verify it against the
  18.0 tree before committing.
