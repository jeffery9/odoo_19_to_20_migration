# Module / model / field mapping (17 → 18)

> OCA 18.0 guide is explicit: this step covers **framework changes**, not the (very large)
> data-model changes. Business-model renames live in OCA OpenUpgrade's `upgrade_analysis.txt`
> per core module. Only **framework-level, cross-module** renames are listed here.

## 1. Framework-level rename table — CONFIRMED

| 17 | 18 | version | source |
|---|---|---|---|
| `<tree>` view type | `<list>` | 18.0 | PR #159909 (codemod `17.5-01`) |
| `<tree colors="...">` | `<list decoration-*>` | 18.0 | 18.0 `ir_ui_view.py` (no `colors` handling) |
| `tree_view_ref` (context) | `list_view_ref` (context) | 18.0 | OCA |
| `def name_get` | `display_name` / `_compute_display_name` | 18.0 | #122085→removed |
| `def _name_search` | `def _search_display_name` | 18.0 | #174967 |
| `check_access_rights()` / `check_access_rule()` | `check_access(op)` | 18.0 | #179148 |
| `_filter_access_rules*()` | `_filtered_access(op)` | 18.0 | #179148 |
| `user_has_groups()` | `self.env.user.has_group()` | 18.0 | #151597 |
| `check_recursion()` | `has_cycle()` | 18.0 | OCA |
| field `group_operator=` | field `aggregator=` | 17.2 | #127353 |
| domain operator `inselect` | `in` + `Query`/`SQL` | 17.4 | #171371 |
| module-level `_()` | `self.env._()` | 18.0 | #174844 |
| `@http.route(type='json')` | `type='jsonrpc'` | 18.1 | #183636 |
| `copy_data` single return | `copy_data` returns list | 18.0 | #154132 |

## 2. Module renames in manifest `depends` — none at framework level

Unlike 18→19 (`web_editor` split into `html_editor`/`html_builder`), **17→18 has no core
module rename**. `web_editor` still exists in 18 (removed only in 19). Third-party apps are the
main blocker: each paid/OCA app needs an 18.0 branch or the upgrade cannot complete.

## 3. Data-model renames — see OpenUpgrade

`account.*` / `stock.*` / `hr.*` field renames are module-specific and out of scope here.
Consult OCA OpenUpgrade `upgrade_analysis.txt` for the exact per-module deltas.

## 4. Symptom → fix index

| 18 install/runtime symptom | likely cause | fix anchor |
|---|---|---|
| `ValueError: Wrong value for ir.ui.view.type: 'tree'` | `<tree>` not renamed | `views-qweb.md` §1 |
| list rows not colored | `colors=` not renamed | `views-qweb.md` §2 |
| `AttributeError: name_get` / bad display name | `name_get` removed | `orm-api.md` §1 |
| name search broken | `_name_search` removed | `orm-api.md` §2 |
| `AttributeError: check_access_rights` | use `check_access` | `orm-api.md` §3 |
| `AttributeError: user_has_groups` | use `env.user.has_group` | `orm-api.md` §3 |
| `AttributeError: check_recursion` | use `has_cycle` | `orm-api.md` §4 |
| field `group_operator` warning/fail | use `aggregator` | `orm-api.md` §6 |
| search on non-stored related field throws | override `search_fetch` | `orm-api.md` §9 |
| route import-time deprecation | `type='json'`→`jsonrpc` | `http-rpc-mail.md` §1 |
| window action still shows tree view | `view_mode` not renamed | `views-qweb.md` §1 |
| inherited view XPath fails | `//tree` not renamed | `views-qweb.md` §1 |
