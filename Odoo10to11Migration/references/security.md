# 10→11 安全 / res.groups 映射表（源码核对版）

> 来源：OCA 10.0 指南 + 11.0 源码核对。
> 作用域：仅 10→11。`security/ir.model.access.csv` 列结构（perm_*）不变。

## 1. 安全组改名  — CONFIRMED

| 10.0 | 11.0 | 备注 |
|---|---|---|
| `base.group_configuration` | `base.group_system` | 配置权限组改名 |

- 所有引用 `base.group_configuration` 的 `ir.model.access.csv` / 安全 XML / `res.groups` `implied_ids` 需改为 `base.group_system`。
- 扫描 id：`group-config`（正则 `base\.group_configuration`）。

## 2. 9→10 遗留的安全组模块化（若尚未迁移需补齐）  — CONFIRMED

| 旧（≤9.0，`base` 前缀） | 新（10.0+ 模块化） |
|---|---|
| `base.group_sale_salesman` | `sales_team.group_sale_salesman` |
| `base.group_sale_salesman_all_leads` | `sales_team.group_sale_salesman_all_leads` |
| `base.group_sale_manager` | `sales_team.group_sale_manager` |
| `base.group_hr_user` | `hr.group_hr_user` |
| `base.group_hr_manager` | `hr.group_hr_manager` |
| `menu_hr_configuration` | `menu_human_resources_configuration` |
| `website.salesteam_website_sales` | `sales_team.salesteam_website_sales` |
| `product.prod_config_main` | `sale.prod_config_main` |

- 这些在 9→10 已迁移；若 10→11 升级链路中模块仍用旧 ID，会触发 `External ID not found`，须一并修正。

## 3. 红线

- `res.groups` 权限列结构 10→11 不变；18→19 的 `res.groups` 权限调整、19→20 的 `ir.model.access.csv` 转换不属本卷。
