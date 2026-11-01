# Reference: Security & res.groups (15 → 16)

Scope: **15.0 → 16.0 only.**

## Conclusion: security model is UNCHANGED in 15→16

- `security/ir.model.access.csv` column format **unchanged** (`perm_read/perm_write/perm_create/perm_unlink`).
- `res.groups` fields `category_id` / `groups_id` / `users` **unchanged**.
- Do NOT apply 19→20 changes here (`category_id`→`privilege_id` refactor, `ir.model.access.csv`→
  `ir.access.csv`) — those are 18→19+ concerns and would be wrong on 16.

## `[verify]` record-rule `global` attribute behavior

DeployMonkey: in 16.0 the `global` attribute on `ir.rule` "now means the rule applies to all users,
including superuser in some contexts." If a custom `ir.rule` uses `global`, verify its effect
range on a 16.0 instance. Single community source → `[verify]`.

## `[EE-verify]`

Enterprise-specific security/permission tweaks in 15→16 — verify against the EE 16.0 tree.
CE surface has no change.
