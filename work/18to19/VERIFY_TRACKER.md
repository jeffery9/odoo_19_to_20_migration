# 18→19 待核实追踪表（中间产物 · 修订时复用）

> 本表汇总 `Odoo_Migration_Cookbook_18_to_19.md` 与 `Odoo18to19Migration/references/*.md` 中所有未关闭的 `[verify]` / `[EE-verify]` 项。
> 修订 SOP：① 取一项 → ② 去 `odoo/odoo` 的 `18.0` vs `19.0` 比对（EE 项对照 Enterprise 19.0 树）→ ③ 确认后删除 `[verify]` 标记，并在 **Cookbook 与 references 两边同步更新** → ④ 跑 `python3 work/18to19/check_cookbook_consistency.py` 校验一致性。
>
> **本轮核实（2026-11-01）方法**：抓取 `odoo/odoo` `19.0` 分支 raw 源码（`odoo/orm/`、`odoo/addons/base/models/`、`odoo/modules/`）交叉验证；19.0 社区插件路径已迁移（stock/hr 等不在 `odoo/addons/<module>`，API 仅列 `base`+`test_*`），故 stock/hr 模型改名无法公开核实。

## 已关闭项（✅ + 纠正说明）

| # | 项 | 结论 | 核实依据 |
|---|---|---|---|
| 1 | `odoo/conf` 的确切替代 | ✅ 确认移除 → `odoo.tools.config` | 19.0 `odoo/conf/__init__.py` 返回 **404**（ORM 拆入 `odoo/orm/`） |
| 2 | `get_module_resource` 替代名 | ✅ 确认 → `odoo.modules.get_resource_from_path`（已导出）/ `pathlib` | 19.0 `odoo/modules/__init__.py` 导出 `get_resource_from_path` |
| 3 | `check_field_access_rights` → 方法名 | ✅ **纠正**：→ `self._has_field_access(field, mode)`，社区所称 `_check_field_access` **不存在** | 19.0 `orm/models.py` 调用 `_has_field_access`；全文件无 `_check_field_access` |
| 6 | `precompute=True` 默认化 | ✅ **纠正**：默认 **False**（非 True） | 19.0 `orm/fields.py`：`precompute: bool = False` |
| 7 | `compute_sudo` 默认标准化 | ✅ **纠正**：默认跟随 `store`（`False` 非存储 / `True` 存储·related），非一律 True | 19.0 `orm/fields.py`：`attrs['compute_sudo'] = attrs.get('compute_sudo', store)` |
| 12 | `<tree>` → `<list>` 争议 | ✅ 确认移除：`<tree>` 根标签在 19.0 报 `Invalid view type` | 19.0 `ir_ui_view.py` 的 `type` 选单仅含 `list` |
| 13 | `target='inline'` 移除 | ✅ 确认移除（合法值 `current`/`new`/`fullscreen`/`main`） | 19.0 `ir_actions.py` `target` 选单无 `inline` |
| 18 | 属性字段弃用（`fields.Property`） | ✅ **纠正**：`fields.Property` **不是字段类**（`Property` 是 `abc.Mapping` 值包装器）；真正字段 `fields.Properties` 未弃用；codemod 针对旧式 `company_dependent`/`property` 用法 | 19.0 `orm/fields_properties.py` |

## `[verify]` 项（社区单源 / 待 19.0 源码或沙箱确认）

| # | 项 | 当前位置 | 状态 / 备注 |
|---|---|---|---|
| 4 | 裸 `SQL` 对象当 domain leaf 在 19 严格化 | api-deltas §2 | open — `Domain.custom` 在 19→20 落地，18→19 需显式构建 |
| 5 | `@api.model_create_multi` 强制（单记录 `create` 告警） | security § / api-deltas §3 | open — **源码复核 `decorators.py` 未见硬告警**，疑不实；保留装饰器即可 |
| 8 | 视图 `<record>` 应声明 `model` | views §4 | open — 19.0 `ir_ui_view.py` 显示 `model` 非 `required`，疑不实 |
| 9 | XPath 表达式校验更严 | views §4 | open |
| 10 | `groups=` 严格校验（对照既有 group XML-ID） | views §4 | open |
| 11 | `oe_button_box` 无 `name` 不再支持 | views §4 | open — 19.0 `ir_ui_view.py` 未见此校验，疑非真实改动 |
| 14 | `stock.quant.package` → `stock.package` | modules-mapping §2 | open — 19.0 社区插件路径已迁移，公开 raw 无法定位；社区(SDLC)称 19.0 改名 |
| 15 | `procurement.group` → `stock.reference` | modules-mapping §2 | open — 同上，待 19.0 树核实 |
| 16 | `hr.contract` → `hr.version` | modules-mapping §4 | open — 19.0 插件路径迁移，待核实 |
| 17 | `hr.candidate` → `hr.applicant` | modules-mapping §4 | open — **作用域风险**：该改名早于 18.0，疑非 18→19 专属；采用前确认 |

## `[EE-verify]` 项（Enterprise 专属 · 需对照 EE 19.0 树）

| # | 项 | 当前位置 | 状态 |
|---|---|---|---|
| E1 | `account_auto_transfer` → `account_transfer` | modules-mapping §6.1 | open — LineScripts 社区确认，待 EE 19.0 树复核 |
| E2 | `account_disallowed_expenses` → `account_fiscal_categories` | modules-mapping §6.1 | open — 同上 |
| E3 | `hr_work_entry_contract_*` 去 `contract` 中缀 | modules-mapping §6.1 | open — 同上 |
| E4 | 其他 EE 模块改名 | modules-mapping §6.1 | open — 同上 |

> 关闭的项请在状态列标 ✅ 并注明核实 commit / 来源，便于追溯。
