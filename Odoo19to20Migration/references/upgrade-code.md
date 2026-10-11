# odoo-bin upgrade_code (bundled codemods)

Codemod repo at `odoo/upgrade_code/`; scripts `{version}-{seq}-{name}.py` expose
`upgrade(file_manager)`. Command exists in 19 and 20 and also runs standalone.
Rewrites addon sources in place: `.py .js .css .scss .xml .csv .po .pot`.

## Commands
```bash
odoo-bin upgrade_code --from 19.0 --addons-path /path/to/addons        # all scripts in [19.0, current]
odoo-bin upgrade_code --script ir-access --addons-path /path/to/addons # single script (substring ok)
odoo-bin upgrade_code --from 19.0 --glob '**/models/*.py' --dry-run    # preview
python3 odoo/cli/upgrade_code.py --from 19.0 --addons-path ...         # standalone (resolved paths)
```
- `--from`/`--script` mutually exclusive, one required; `--to` inclusive, default = running release.
- Prints `updated:`/`deleted:` per file; **exit code 1 when anything changed** (CI gate).
- Best-effort helpers, "not silver bullets": review `git diff` on a clean branch first.
- Codemods fix source only; DB data upgrades stay in module `pre/post` scripts.

## Scripts selected for a 19 → 20 run
| Script | Rewrites |
|---|---|
| `17.5-01-tree-to-list` | view mode `tree`→`list` (view_mode/binding fields, archs) |
| `18.1-00-sql-constraint` | `_sql_constraints = [...]` → `models.Constraint(...)` |
| `18.1-02-route-jsonrpc` | route `type='json'` → `type='jsonrpc'` |
| `18.2/18.3 l10n` | chart-template records; fiscal-position tax mapping (`tax_src_id`/`tax_dest_id` → alternative-tax columns) |
| `18.5-00-domain-dynamic-dates` | inline unary-minus constants in domains; `18.5-00-no-tax-tag-invert` tax `formula` signs; `18.5-00-deprecated-properties` deprecated property fields |
| `19.1-00-t-call` | hoist `t-set` before the `t-call`/`t-snippet-call` consuming it (Owl 3) |
| `19.3-00-account-groups` | `account.group` CSV/data → `account.account` hierarchy + `parent_id` |
| `19.3-00-account-report-foldable` | normalize `foldable` XML value to bool |
| `19.3-00-base64-in-xml` | inline `type="base64" … file=` payloads → 20 loading form |
| `19.4-00-ir-access` | `ir.model.access.csv` + `<record model="ir.rule">` XML → `security/ir.access.csv` (`crud` ops, normalized domains) |
| `19.4-00-ormcache-on-transaction` | `registry.clear_cache` → `transaction.invalidate_ormcache` |
| `19.5-00-tuple-rec_names_search` | `_rec_names_search = ['name']` → tuple |
| `20.0-00-search-date-filters` | drop `start_month`/`end_month`-style attrs from `date` search filters |

No version prefix (never auto-selected): `owl3-migration.py` (run via
`--script owl3-migration`), helpers `tools_etree.py`, `tools_js_expressions.py`
(importable as `odoo.upgrade_code.tools_etree` etc.).

## Writing your own script
```python
def upgrade(file_manager):
    files = [f for f in file_manager if f.path.suffix == '.py']
    for fileno, file in enumerate(files, start=1):
        content = file.content                      # lazy read
        file.content = content.replace('old_api(', 'new_api(')
        file_manager.print_progress(fileno, len(files))
```
- File object: `path` (pathlib), `addon`, lazy `content` (assign unchanged = no-op;
  assign `None` = delete on save).
- Manager: iteration, `len`, `get_modules()`, `get_file(module, name)`,
  `add_to_summary(msg)` (printed at end), `print_progress(cur, total, file_name)`.
- Custom scripts must live **inside** `odoo/upgrade_code/` (`--script` refuses
  paths outside it); alternatively call `odoo.cli.upgrade_code.migrate(...)` from Python.

## Suggested workflow
1. `--dry-run` → 2. real run on clean branch → 3. review/commit diff →
4. `-u` registry upgrade + tests → 5. re-run this skill's scanner (expect 0).
