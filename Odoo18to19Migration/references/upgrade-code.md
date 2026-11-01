# upgrade_code codemods (18 → 19)

## 1. Running the codemod

`odoo-bin upgrade_code` is Odoo's bundled source-rewrite tool (present in 19.0). For
18→19 it must be run **from a 19.0 installation** against 18 source:

```bash
# dry-run first, on a clean git branch
odoo-bin upgrade_code --from 18.0 \
  --addons-path /path/to/addons --dry-run

# then the real run
odoo-bin upgrade_code --from 18.0 \
  --addons-path /path/to/addons

# scope to one module
odoo-bin upgrade_code --from 18.0 --addons-path /path/to/addons -m my_module
```

- Codemods rewrite **Python/XML source only**; they do not perform data migrations.
  Data upgrades stay in the module's `migrations/19.0/` scripts.
- Review `git diff` file by file and commit on a dedicated branch.

## 2. Which scripts actually run for 18→19

`upgrade_code` selects scripts whose version is `∈ [--from, --to]`. For a **pure
18.0 → 19.0 CE** run (`--from 18.0 --to 19.0`), only scripts with version `≤ 19.0`
apply. From the 19.0 `odoo/upgrade_code/` inventory, the 18→19-relevant scripts are:

| Script | Rewrites |
|---|---|
| `18.1-00-sql-constraint` | `_sql_constraints = [...]` → `models.Constraint(...)` (security-and-orm §3) |
| `18.1-02-route-jsonrpc` | route `type='json'` → `type='jsonrpc'` (binary-http-mail §1) |
| `18.2 / 18.3 l10n` | chart-template records; fiscal-position tax mapping (`tax_src_id`/`tax_dest_id` → alternative-tax columns) |
| `18.5-00-domain-dynamic-dates` | inline unary-minus constants in domains |
| `18.5-00-no-tax-tag-invert` | tax `formula` sign fixes |
| `18.5-00-deprecated-properties` | deprecated property fields (api-deltas §4) |

> **Scope guard:** scripts `19.1-00-t-call` (Owl 3 `t-set` hoist), `19.3-00-account-groups`,
> `19.3-00-account-report-foldable`, `19.3-00-base64-in-xml`, `19.4-00-ir-access`, etc. have
> version **> 19.0** and therefore do **NOT** run for a plain 18→19 CE upgrade. They apply
> only when `--to ≥ 19.x` (Online) or when upgrading onward to 20.0 — handle those in the
> corresponding skill.

## 3. Items the codemod will NOT fix (manual)

These need human edit, guided by the other reference files:

- `web_editor` → `html_editor`/`html_builder` manifest repoint (modules-mapping §1).
- Owl 2 → Owl 3 JS rewrites + `t-esc`→`t-out` / `t-set` hoist (views-qweb-owl §1–2).
- `@api.returns` removal, `odoo/orm` package internal-import removals (security-and-orm §4).
- `res.groups` / `res.users` field renames and model/field renames (modules-mapping §3–4).
- `_apply_ir_rules` → `_search` and `authenticate()` signature (security-and-orm §4, binary-http-mail §2).
- Deprecation cleanups (`self._cr`→`self.env.cr`, etc.) — may be partially scripted; verify.

## 4. Scanner contract

The bundled `scripts/scan_addon.py` (copied verbatim from the 19→20 skill — it is
version-agnostic) flags findings and prints the 19.0 replacement + whether a codemod
covers it:

```bash
python3 scripts/scan_addon.py /path/to/addons --addon my_module --json
# exit code 1 = findings present
```

## 5. Writing your own script

To add a custom 18→19 rewrite, drop a script under the 19.0 `odoo/upgrade_code/`
layout (or a local `migrations/19.0/` pre/init script for data) and re-run. Keep each
script single-purpose and idempotent; commit the resulting `git diff` with the anchor
from the relevant `references/*.md` file.
