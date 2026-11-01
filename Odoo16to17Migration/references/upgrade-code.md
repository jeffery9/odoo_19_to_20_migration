# 16→17 upgrade_code codemod status

## Reality: 17.0 has NO upgrade_code codemod

Verified: the `odoo/upgrade_code/` module **does not exist** in the 17.0 branch
(GitHub directory listing 404; `odoo/upgrade_code/__init__.py` 404). The
`odoo-bin upgrade_code` tooling and its bundled scripts (`17.5-*` etc.) were
introduced in **18.0**. Therefore:

- There is **no `odoo-bin upgrade_code --from 16.0`** step for 16→17.
- All fixes are **manual** (no `auto` mode in this skill's scanner).
- This is the lowest-automation pair of the workspace (vs 17→18: 1 codemod;
  18→19: many codemods).

## What to do instead

1. **Triage** with the bundled scanner (`scripts/scan_addon.py`) — flags every
   16→17 break with the 17.0 replacement.
2. **Manual mappings** from the other reference files
   (views-qweb / orm-api / http-rpc-mail / security / modules-mapping).
3. **Data/structure migrations** go in each module's `migrations/17.0/`
   directory:
   - `pre-17.0.py` (db pre-processing), `post-17.0.py` (post-install data),
     `end-17.0.py` (finalize).
   - Each script is single-responsibility, idempotent; receives `cr`/`env`.
4. **Validate**: re-run scanner (expect 0), `odoo-bin -u MY_MODULE
   --test-tags /MY_MODULE`, start with `--dev=all` and clear every
   `DeprecationWarning` (`name_get`, `get_resource_path` warnings are 17→18
   precursors). Module data migrations live under `MY_MODULE/migrations/17.0/`.

## Writing your own migration scripts

Place under `<module>/migrations/17.0/`. Example `post-17.0.py`:

```python
def migrate(cr, version):
    # idempotent data fixup; use cr.execute / env
    pass
```

Commit the resulting `git diff` with the relevant `references/*.md` anchor cited.
