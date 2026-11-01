# Security & `res.groups` (17 → 18) — UNCHANGED

> Unlike the 18→19 and 19→20 steps, **17→18 changes nothing about the security file format
> or the `res.groups` model.** Do not apply later-step renames here.

## 1. Access file `ir.model.access.csv` is UNCHANGED

17 and 18 both use `security/ir.model.access.csv` with the `perm_*` columns:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_lock,my.lock,model_my_lock,base.group_user,1,1,1,0
```

Do **not** apply the 19→20 `ir.access.csv` / `operation` conversion — that is a 20.0-only
change (codemod `19.4-00-ir-access`, irrelevant to 17→18).

## 2. `res.groups` model is UNCHANGED

In 17→18 there is **no** `category_id`→`privilege_id` refactor (that is 19.0). The fields
`res.groups.category_id` / `groups_id` / `users` and `res.users.groups_id` keep their 17 names.

## 3. The only security-relevant API change is the access-check merge

`check_access_rights` / `check_access_rule` → `check_access(op)`, etc. See `orm-api.md` §3.
This simplifies permission checks but does **not** alter model/field structure.
