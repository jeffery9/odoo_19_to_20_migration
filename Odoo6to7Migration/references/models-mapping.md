# 6→7 模块 / 模型 / 字段映射表（源码核对版）

> 来源：OpenERP 7.0 Release Notes + 论坛 v6→v7 讨论 + 7.0 源码核对。
> 作用域：仅 6→7。本卷最大模型层改动是 `res.partner.address` 合并与 Manifest 键统一。

## 6.0 → 7.0 映射总表

| 6.0 | 7.0 | 类别 | 可信度 |
|---|---|---|---|
| `osv.osv` 基类 | `osv.Model` | ORM 基类 | CONFIRMED |
| `osv.osv_memory` 基类 | `osv.TransientModel` | ORM 基类 | CONFIRMED |
| `res.partner.address` 模型 | 移除；字段并入 `res.partner` | 模型移除 | CONFIRMED |
| `res_partner_address` 表 | 并入 `res.partner` | 数据库表 | CONFIRMED |
| `__openerp__.py` `init_xml` 键 | 合并进 `data` | Manifest 键 | CONFIRMED |
| `__openerp__.py` `update_xml` 键 | 合并进 `data` | Manifest 键 | CONFIRMED |
| `__openerp__.py` `demo_xml` 键 | 合并进 `data` | Manifest 键 | CONFIRMED |
| 视图无 `version` | `version="7.0"` + `sheet` | 视图属性 | CONFIRMED |

## `res.partner.address` 合并细节（CONFIRMED）

- 6.0：`res.partner` 与 `res.partner.address` 两个模型，一个 partner 可有多个 address 记录（`partner_id` 外键）。
- 7.0：`res.partner.address` 删除，街道/城市/邮箱/电话等字段直接落在 `res.partner` 上。
- 迁移动作：代码中所有 `res.partner.address` / `res_partner_address` 引用改为 `res.partner` 字段；视图、报表、关联字段（`many2one` 指向 `res.partner.address`）一并改写。
- 数据库并入动作由 OpenUpgrade 执行（本卷不覆盖 DB）。

## Manifest 键统一（CONFIRMED）

- `init_xml` / `update_xml` / `demo_xml` 的内容全部并入 `data` 列表。
- 文件名仍是 `__openerp__.py`（改名 `__manifest__.py` 是 **9→10**，不在本卷）。
- 扫描 id：`manifest-keys`（正则 `update_xml|init_xml|demo_xml`）。

## 本卷不涉及的重大重命名（红线，属更晚版本）

- `openerp` → `odoo` → 9→10；
- `osv.Model` → `models.Model` / `@api.*` / `self.env` → 7→8；
- `@api.one` 移除 / `fields.Date` 对象化 → 11→12；
- `__openerp__.py` → `__manifest__.py` → 9→10。
