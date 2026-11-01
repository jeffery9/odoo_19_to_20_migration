# upgrade_code codemods (17 → 18)

## 1. Running the codemod

`odoo-bin upgrade_code` is Odoo's bundled source-rewrite tool. For 17→18 it is run **from an
18.0 installation** against 17 source:

```bash
# dry-run first, on a clean git branch
odoo-bin upgrade_code --from 17.0 \
  --addons-path /path/to/addons --dry-run

# then the real run (renames tree->list only)
odoo-bin upgrade_code --from 17.0 \
  --addons-path /path/to/addons

# scope to one module / run just the script
odoo-bin upgrade_code --from 17.0 --addons-path /path/to/addons -m my_module
odoo-bin --addons-path=${YOUR_PROJECT} upgrade_code --script 17.5-01-tree-to-list.py
```

- Codemods rewrite **Python/XML/JS source only**; data migrations stay in `migrations/18.0/`.
- Review `git diff` file by file (community reports `editable`/`create`/`default_order`
  attributes sometimes land outside the tag → malformed XML — eyeball the diff).
- The 18.0 tree does **not** contain `17.5-01-tree-to-list` under an Online-prefixed folder;
  it lives directly at `odoo/upgrade_code/17.5-01-tree-to-list.py`.

## 2. Which scripts actually run for 17→18

18.0 `odoo/upgrade_code/` inventory (verified via GitHub API on the `18.0` branch):

| Script | Rewrites | runs for 17→18? |
|---|---|---|
| `17.5-00-example.py` | template, **not** a real codemod | no |
| `17.5-01-tree-to-list.py` | `<tree>`→`<list>` (XML/Python/JS, skips tree-named XML-IDs) | **yes (only one)** |

> **Scope guard:** `18.1-00-sql-constraint`, `18.1-02-route-jsonrpc`, `18.5-*` etc. are
> **NOT** in the 18.0 tree — they ship in the 19.0 tree for the 18→19 step. So 17→18 has
> **no codemod** for `models.Constraint`, `type='json'`→`jsonrpc`, or any other rename; those
> are manual (see `orm-api.md`, `http-rpc-mail.md`).

## 3. Items the codemod will NOT fix (manual)

- `name_get` → `display_name` / `_search_display_name` (`orm-api.md` §1–2)
- `check_access_rights`/`check_access_rule`/`user_has_groups`/`check_recursion` → new APIs (`orm-api.md` §3–4)
- `group_operator` → `aggregator` (`orm-api.md` §6)
- `colors` → `decoration-*` (`views-qweb.md` §2)
- `type='json'` → `type='jsonrpc'` (`http-rpc-mail.md` §1)
- `kanban-box` → `card` (`views-qweb.md` §5, `[verify]` version scope)
- `states` attr / `fields_view_get` (`views-qweb.md` §6–7, `[verify]`)

## 4. Scanner contract

The bundled `scripts/scan_addon.py` (version-agnostic) flags findings and prints the 18.0
replacement + whether a codemod covers it:

```bash
python3 scripts/scan_addon.py /path/to/addons --addon my_module --json
# exit code 1 = findings present
```

## 5. Writing your own script

Drop a custom rewrite under the 18.0 `odoo/upgrade_code/` layout (or a local
`migrations/18.0/` pre/init data script) and re-run. Keep each script single-purpose and
idempotent; commit the `git diff` with the anchor from the relevant `references/*.md` file.
