# 5→6 安全 / res.groups 映射表（源码核对版）

> 来源：OpenERP 5.0/6.0 源码核对。
> 作用域：仅 5→6。`security/ir.model.access.csv` 列结构（perm_*）不变。

## 1. 安全组与访问权限  — CONFIRMED（不变）

- 5.0/6.0 的 `security/ir.model.access.csv` 列结构一致：
  `id` / `name` / `model_id:id` / `group_id:id` / `perm_read` / `perm_write` /
  `perm_create` / `perm_unlink`。
- `res.groups` 模型在 5→6 基本不变。

## 2. 迁移要点

- 只需确认 XML-ID 仍指向存在的 `res.groups` 记录；无需改动列结构或权限语义。
- 6.0 起权限体系逐步细化，但 5→6 区间内无破坏性调整。

## 3. 红线

- `res.groups` 重大权限调整 → 18→19；`ir.model.access.csv` 转换 → 19→20；
  这些均不属 5→6。
