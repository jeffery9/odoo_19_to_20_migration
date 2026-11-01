# 9→10 安全 / res.groups 映射表（源码核对版）

> 来源：OCA `Migration to version 10.0` + Odoo 10.0 源码核对。
> 作用域：仅 9→10。`security/ir.model.access.csv` 列结构（perm_*）不变。

## 1. 安全组改名  — CONFIRMED

| 9.0 | 10.0 | 备注 |
|---|---|---|
| `base.group_configuration` | `base.group_system` | 配置权限组改名 |

- 所有引用 `base.group_configuration` 的 `ir.model.access.csv` / 安全 XML / `res.groups` `implied_ids` 需改为 `base.group_system`。
- 扫描 id：`group-config`（正则 `base\.group_configuration`）。

## 2. 安全组模块化（从 `base` 迁移到各模块）  — CONFIRMED

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

- `sales_team.group_sale_salesman`、`sales_team.group_sale_salesman_all_leads`、`sales_team.group_sale_manager` 取代原 `base.group_sale_*` 三个组。
- `hr.group_hr_user`、`hr.group_hr_manager` 取代原 `base.group_hr_*` 两个组。
- `menu_hr_configuration` 菜单 ID 改名为 `menu_human_resources_configuration`。
- `website.salesteam_website_sales` 迁到 `sales_team.salesteam_website_sales`。
- `product.prod_config_main` 配置菜单迁到 `sale.prod_config_main`。
- 扫描 id：`group-move`（正则覆盖上述 8 个旧 ID）。

## 3. 红线

- `res.groups` 权限列结构 9→10 不变；18→19 的 `res.groups` 权限调整、19→20 的 `ir.model.access.csv` 转换不属本卷。
