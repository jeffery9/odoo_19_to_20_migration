# 17→18 待核实追踪表（中间产物 · 修订时复用）

> 本表汇总 `Odoo_Migration_Cookbook_17_to_18.md` 与 `Odoo17to18Migration/references/*.md` 中所有未关闭的 `[verify]` 项。
> 修订 SOP：① 取一项 → ② 去 `odoo/odoo` 的 `17.0` vs `18.0` 比对（EE 项对照 Enterprise 18.0 树）→ ③ 确认后删除 `[verify]` 标记，并在 **Cookbook 与 references 两边同步更新** → ④ 跑 `python3 work/17to18/check_cookbook_consistency.py` 校验一致性。
>
> **本轮核实（2026-11-01）方法**：抓取 `odoo/odoo` `18.0` 分支 raw 源码（`odoo/addons/base/models/ir_ui_view.py`、`odoo/models.py`、`odoo/release.py`、`odoo/upgrade_code/`）交叉验证；已确认核心移除与 `tree`→`list` 改名。

## 已关闭 / 已确认项（本轮核实）

| # | 项 | 结论 | 核实依据 |
|---|---|---|---|
| 1 | `tree`→`list` 视图类型改名 | ✅ 确认：18.0 `ir_ui_view.py` `type` 选单仅含 `list`；codemod `17.5-01-tree-to-list.py` 存在于 18.0 树 | GitHub 18.0 源码 + GitHub API 目录列举 |
| 2 | `name_get` / `_name_search` / `check_access_rights` / `check_access_rule` / `user_has_groups` / `check_recursion` 移除 | ✅ 确认移除（18.0 `models.py` 无对应 `def`；新 API `check_access`/`_filtered_access`/`has_group`/`_search_display_name` 被调用） | 18.0 `models.py` + changelog #122085/#174967/#151597/#179148 |
| 3 | `colors` 属性移除 → `decoration-*` | ✅ 确认：18.0 `ir_ui_view.py` 仅处理 `decoration-*`，无 `colors` 分支 | 18.0 `ir_ui_view.py` 源码 |
| 4 | `upgrade_code` codemod 范围 | ✅ 确认：17→18 唯一真实 codemod = `17.5-01-tree-to-list`（`17.5-00-example.py` 为模板非真实） | 18.0 `upgrade_code/` 目录列举 |
| 5 | `aggregator` / `inselect` 移除 / `check_access` 合并 / `_search_display_name` / `has_cycle` / `env._()` / `type='jsonrpc'` | ✅ 确认（官方 changelog + 社区交叉） | odoo.com/18.0 changelog #127353/#171371/#179148/#174967/#154132/#174844/#183636/#159909 |

## `[verify]` 项（社区单源 / 待 18.0 源码或沙箱确认）

| # | 项 | 当前位置 | 状态 / 备注 |
|---|---|---|---|
| 1 | **PostgreSQL 14+** 运行下限 | §1.2 | open — 18.0 弃用 PG 12/13（DeployMonkey 单一来源）；具体下限待 `odoo/sql_db.py` 版本校验确认 |
| 2 | **`kanban-box`→`card` 版本归属** | §4.5 / `views-qweb.md` §5 | open — OCA 列为 18.0；但 18→19 烹饪书（19.0 源码核实）归因于 Owl 3 重写（19.0）。采纳 `kanban-box`→`card`，但须以 18.0 实际模板为准 |
| 3 | **`states` 字段属性移除** | §4.6 / `views-qweb.md` §6 | open — 仅 DeployMonkey 报告，未见于 18.0 官方 changelog |
| 4 | **`fields_view_get`→`get_views`** | §4.7 / `views-qweb.md` §7 | open — 仅 DeployMonkey 报告，OCA 18.0 指南未列 |
| 5 | **资产/SCSS bundle 重构** | §4.8 | open — DeployMonkey 报告 18 重组子 bundle / 重命名 SCSS 变量 / 改 `__manifest__.py` asset 语法；前端破坏性，建议实机升级人眼核对 |
| 6 | **`_sql_constraints` 同名校验更严** | §2.7 | open — DeployMonkey：重复约束名升级时报错；保留唯一命名即可 |

## 备注

- 17→18 的 `[verify]` 远少于 18→19（18→19 含 13 CE + 4 EE）。原因：17→18 的破坏面以"官方 changelog 明确移除/改名"为主，社区交叉度高；残余 `[verify]` 集中在前端/基础设施层（PG、kanban、states、asset），这些本就非核心 ORM/视图路径。
- 17→18 **无 Enterprise 专属** `[EE-verify]` 项：本步企业版与社区版的破坏面一致（安全模型/数据模型的大改在 18→19 才发生）。
- 关闭的项请在状态列标 ✅ 并注明核实 commit / 来源，便于追溯。
