---
name: odoo_16_to_17_migration
description: Migrates custom Odoo 16.0 addons to 17.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 16 to 17, fix 17.0 hard breaks (attrs/states attributes rejected with ValidationError, list invisible->column_invisible, res.config.settings simplified, hooks (cr,registry)->env, get_resource_path->file_path, active_id/active_ids/active_model context, message_post body format), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 16-only APIs. Note 17.0 has NO upgrade_code codemod — all fixes are manual.
version: 17.0.1
author: Independent (companion to the Odoo Migration Cookbook series)
category: migration
odoo_versions: ["16.0", "17.0"]
tags: [odoo, migration, upgrade, views, qweb, orm, hooks, mail, codemod, upgrade_code]
---

# Odoo 16 → 17 Migration

## Goal

Take a 16.0 custom addon (or a whole addons tree) to 17.0 with no leftover
16-only API, using **verified manual mappings** (there is **no** `upgrade_code`
codemod for 16→17 — the tooling ships in 18.0).

> **Scope note.** This skill covers the **16.0 → 17.0** jump only. The 17→18
> skill (`Odoo17to18Migration/`) handles the next step (tree→list, name_get
> REMOVAL, check_access_rights/user_has_groups/check_recursion removal,
> inselect removal, aggregator rename). Many items that changed *after* 17.0
> (e.g. `aggregator` rename in 17.2, `type='json'`→`jsonrpc` in 18.1) are
> listed here ONLY where they are explicitly out of 16→17 scope — see the
> red lines below.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  16→17 jump. Primary anchors:
  - OCA `maintainer-tools`《Migration to version 17.0》framework list
    (PR #104741, #106425, #122085, #135607, b4a7996, daf05d48).
  - GitHub `odoo/odoo` branch `17.0` source (verified `ir_ui_view.py` raises
    `ValidationError: "Since 17.0, the 'attrs' and 'states' attributes are no
    longer used."`; `type` selection still contains `('tree','Tree')`;
    `tools/misc.py` removes `get_resource_path` and defines `file_path`;
    `requirements.txt` keeps `libsass` and pins `Werkzeug==2.0.2`;
    `odoo/upgrade_code/` is ABSENT).
  - Community cross-checks: odoohub version diff, Medium《Odoo Migration
    Decoded》, LobeHub frontend skill, oec.sh requirements.
- Items tagged **[EE-verify]** are Enterprise-only: re-check against the
  matching EE 17.0 tree before deployment. Items tagged **[verify]** come from
  a single community source or sources that disagree (Bootstrap 5/jQuery scope,
  Werkzeug 1.x impact, PG floor) — confirm before relying on them.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 17.0 replacement, and notes every item is `manual`
   (no codemod exists for 16→17).
2. **Manual mappings** — for every finding, apply the replacement from the
   matching reference file:
   - views / QWeb / frontend / settings → `references/views-qweb.md`
   - ORM & Python API (name_get, hooks, get_resource_path, active_* context) → `references/orm-api.md`
   - HTTP/RPC/mail/binary → `references/http-rpc-mail.md`
   - security file & `res.groups` (unchanged in 16→17) → `references/security.md`
   - module/model/field maps + symptom index → `references/modules-mapping.md`
   - codemod status & `migrations/17.0/` scripts → `references/upgrade-code.md`
3. **Data migrations** — put DB/structure fixes in each module's
   `migrations/17.0/` (`pre-`/`post-`/`end-` scripts). There is no
   `upgrade_code` run for 16→17.
4. **Validate** — re-run the scanner (expect 0 findings), then
   `odoo-bin -u <module> --test-tags /<module>` in a 17.0 sandbox; fix view
   `ValidationError` (attrs/states) and `TypeError` (hook/context signatures)
   first. Start with `--dev=all` and clear every `DeprecationWarning`
   (`name_get`/`get_resource_path` warnings are 17→18 precursors).
5. **Report** — summarize per addon: manual edits (with reference anchor used),
   remaining [EE-verify]/[verify] items, test status.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 17.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **`attrs` / `states` are the headline breaking change.** Any view using them
  throws `ValidationError: Since 17.0, the "attrs" and "states" attributes are
  no longer used.` at install/upgrade. Rewrite as inline `invisible` /
  `readonly` / `required` Python expressions.
- **There is NO `upgrade_code` codemod for 16→17** — `odoo/upgrade_code/` does
  not exist in 17.0. Do not tell the user to run `odoo-bin upgrade_code
  --from 16.0`; all fixes are manual.
- **`<tree>` is STILL valid in 17.0** (`type` selection contains `tree`). Do
  NOT rename `<tree>`→`<list>` here — that is the 17→18 step. Only change
  `invisible="1"`→`column_invisible="1"` inside list views.
- **SCSS still compiles in 17.0** (`libsass` is in `requirements.txt`). Do NOT
  rewrite `.scss`→`.css` during 16→17 (that removal is post-17.0).
- **Do NOT migrate these in 16→17** (they are still valid in 17.0; their
  removal/rename belongs to 17→18 or later): `check_access_rights` /
  `check_access_rule` / `user_has_groups` / `check_recursion` / `_name_search`
  / `inselect` operator; field `group_operator` (renamed `aggregator` only in
  17.2); `@http.route(type='json')` (renamed `jsonrpc` only in 18.1);
  `mail.channel` (renamed `discuss.channel` only in 18.0); `web_editor`
  (split only in 19.0). `name_get` is only *deprecated* in 17 (still works,
  warns) — migrate it but do not treat removal here.
- **Security file & `res.groups` are UNCHANGED in 16→17.** Keep
  `security/ir.model.access.csv` with `perm_*` columns; do not apply the
  19→20 `ir.access.csv`/`operation` conversion.
- Python 3.10+ is required (3.8/3.9 dropped) — confirm the runtime before migrating.
- When copying a value from a clipped/secondary source, verify it against the
  17.0 tree before committing.
