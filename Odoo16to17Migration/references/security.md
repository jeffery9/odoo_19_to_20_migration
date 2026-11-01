# 16→17 Security & res.groups (UNCHANGED)

**Conclusion: 16→17 does not change the security file format or the `res.groups`
model.** This reference exists only to mark the red line so 16→17 migrations do
not accidentally apply later-version security refactors.

- `security/ir.model.access.csv` column format is **unchanged**
  (`perm_read/perm_write/perm_create/perm_unlink`).
- `res.groups.category_id` / `groups_id` / `users` fields are **unchanged**.
- The only security-relevant code change in the 16→17 window is the
  `name_get` deprecation (see `orm-api.md`) — it affects display names, not the
  security model.

## What is NOT in 16→17 (later-version red lines)

| Change | Real version | Source note |
|---|---|---|
| `res.groups.category_id` → `privilege_id` | 19.0 | 17→18 skill explicitly keeps res.groups unchanged |
| `ir.model.access.csv` → `ir.access.csv` (+ `operation` col) | 19→20 | do NOT apply here |
| `check_access_rights`/`user_has_groups` removal | 18.0 | still valid in 17.0; removal handled by 17→18 |

## [EE-verify]

Enterprise-only permission behavior tweaks in 16→17, if any, must be re-checked
against the EE 17.0 tree before deployment. CE-level security is unchanged.
