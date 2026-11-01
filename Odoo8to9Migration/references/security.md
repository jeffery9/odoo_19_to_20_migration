# 8→9 安全 / res.groups 映射表（源码核对版）

> 来源：8.0/9.0 源码核对 + Odoo 9.0 Release Notes。
> 作用域：仅 8→9。`security/ir.model.access.csv` 列结构（perm_*）不变。

## 1. 安全组与访问权限  — CONFIRMED（基本不变）

- `security/ir.model.access.csv` 列结构（`perm_read` / `perm_write` / `perm_create` / `perm_unlink`）在 8→9 **不变**。
- `res.groups` 模型与 `implied_ids` 机制 8→9 无破坏性改动。
- 唯一需留意的是 Community/Enterprise 拆分：若自定义模块的安全规则依赖了变为 Enterprise-only 的模块，需一并审视（见 models-mapping.md 第 1 节）。

## 2. 红线

- `res.groups` 权限列结构 8→9 不变；18→19 的 `res.groups` 权限调整、19→20 的 `ir.model.access.csv` 转换不属本卷。
- 9→10 的 group 模块化（如 `base.group_sale_salesman` 等迁移）属 9→10，不在本卷。
