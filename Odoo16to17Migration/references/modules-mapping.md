# 16→17 Module / Model / Field mapping (light)

OCA 17 guide scopes this to **framework changes, not data-model changes**.
Data-model renames live in OCA OpenUpgrade `upgrade_analysis.txt` per core
module. Below are only framework-level, cross-module renames/behaviors.

## Framework-level rename table — CONFIRMED

| 16 | 17 | Version | Source |
|---|---|---|---|
| `attrs="{'invisible':[...]}"` | `invisible="expr"` | 17.0 | PR #104741 |
| `attrs="{'required':[...]}"` | `required="expr"` | 17.0 | PR #104741 |
| `attrs="{'readonly':[...]}"` | `readonly="expr"` | 17.0 | PR #104741 |
| `states="draft,open"` | (removed) → condition expr | 17.0 | PR #104741 + odoohub |
| list field `invisible="1"` | `column_invisible="1"` | 17.0 | OCA 17 |
| `o_setting_*_pane` divs | `<setting>` | 17.0 | PR #106425 |
| `app_setting_block` | `<block>` | 17.0 | PR #106425 |
| `message_post(body="<p>")` | `body_is_html=True` / Markdown | 17.0 | OCA + odoohub |
| `post_init_hook(cr, registry)` | `post_init_hook(env)` | 17.0 | PR b4a7996 |
| `uninstall_hook(cr, registry)` | `uninstall_hook(env)` | 17.0 | PR b4a7996 |
| `get_resource_path(a,b,c)` | `file_path('a/b/c')` | 17.0 | PR #135607 (src-verified) |
| context `active_id` | `id` | 17.0 | PR daf05d48 |
| context `active_model` | hardcoded model name | 17.0 | PR daf05d48 |
| `name_get()` | `_compute_display_name` | 16.4 dep/17 ok | PR #122085 |
| Python 3.8 / 3.9 | Python 3.10+ | 17.0 | release + multi-source |

## Module renames (manifest depends) — none core

No core module rename in 16→17 (unlike 18→19 `web_editor` split). Third-party
apps are the main blocker — each needs a 17.0 branch.

## Symptom → fix index

| 17 symptom | cause | anchor |
|---|---|---|
| `ValidationError: Since 17.0, the "attrs" and "states" attributes are no longer used.` | attrs/states in view | views-qweb.md |
| list shows extra empty column | `invisible="1"` not `column_invisible` | views-qweb.md |
| settings page broken | old panes / app_setting_block | views-qweb.md |
| message body renders raw HTML | `message_post` missing `body_is_html` | http-rpc-mail.md |
| hook `TypeError` | `(cr, registry)` not `env` | orm-api.md |
| `ImportError: get_resource_path` | use `file_path` | orm-api.md |
| smart-button context warning | `active_*` not rewritten | views-qweb.md |
| server won't start (Python) | still on 3.8/3.9 | cookbook §1.1 |
