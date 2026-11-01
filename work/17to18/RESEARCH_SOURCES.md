# 17→18 研究来源查证地图（中间产物 · 修订时复用）

> 本文件是 17→18 迁移 **Cookbook（`Odoo_Migration_Cookbook_17_to_18.md`）** 与 **Skill（`Odoo17to18Migration/`）** 的"查证地图"。
> 用途：将来修订（核实 `[verify]` 项、补充内容、或把 Cookbook 渲染成 PDF）时，直接按本图去对应来源复核，无需从零检索。
> 所有变更最终须对照 `github.com/odoo/odoo` 的 **`17.0` / `18.0`** 分支（EE 项对照 Enterprise 18.0 树）确认。

## 一、官方来源（odoo.com/18.0 ORM Changelog 及 PR）

| PR | 变更 | 归属版本 | 状态 |
|---|---|---|---|
| #122085 | `name_get()` 弃用 | 16.4 弃用，**18.0 移除** | CONFIRMED（移除已核实 18.0 `models.py`） |
| #127353 | `group_operator` → `aggregator` | 17.2 | CONFIRMED |
| #137031 | 视图缺失字段自动补 `invisible` | 18.0 | CONFIRMED |
| #144747 | `_flush_search()` 弃用 | 17.1 | CONFIRMED |
| #151597 | `user_has_groups` 移除 → `env.user.has_group` | 18.0 | CONFIRMED（移除已核实 18.0 `models.py`） |
| #154132 | `copy`/`copy_data` 多记录 | 18.0 | CONFIRMED |
| #159528 | 日期粒度 `month_number`/`quarter_number`/`week_number` | 17.3 | CONFIRMED |
| #159909 | `tree`→`list` 视图类型改名（codemod `17.5-01-tree-to-list`） | 18.0 | CONFIRMED（codemod 文件已核实存在于 18.0 树） |
| #170009 | `Domain` API（`from odoo import Domain`） | 18.1 | CONFIRMED |
| #171371 | `inselect` 运算符移除 | 17.4 | CONFIRMED |
| #174844 | `env._()` 翻译 / `env.translations` | 18.0 | CONFIRMED |
| #174967 | `_name_search` → `_search_display_name` | 18.0 | CONFIRMED（移除已核实 18.0 `models.py`） |
| #179148 | `check_access`/`has_access`/`_filtered_access` 合并 | 18.0 | CONFIRMED（移除已核实 18.0 `models.py`） |
| #183636 | 控制器 `type='json'` → `type='jsonrpc'` | 18.1 | CONFIRMED |

## 二、GitHub 18.0 源码核实记录（2026-11-01）

方法：抓取 `raw.githubusercontent.com/odoo/odoo/18.0` 的源码交叉验证。

| 项 | 核实文件（18.0） | 结论 |
|---|---|---|
| `tree` 视图类型移除 | `odoo/addons/base/models/ir_ui_view.py`：`type` 选单仅 `('list','List'),('form','Form'),…`，无 `'tree'` | `<tree>` 抛 `ValueError: Wrong value for ir.ui.view.type: 'tree'` |
| `colors` 属性移除 | 同上：仅处理 `decoration-*`（`attr.startswith('decoration-')`），无 `colors` 处理分支 | `colors=`→`decoration-*` |
| `name_get`/`_name_search`/`check_access_rights`/`check_access_rule`/`user_has_groups`/`check_recursion` 移除 | `odoo/models.py`：上述 `def` 均不存在；`check_access`/`_filtered_access`/`has_group`/`_search_display_name` 被调用 | 移除确证（注意：文件截断，部分"移除"以官方 changelog 为准） |
| `upgrade_code` 清单 | `odoo/upgrade_code/` 目录（GitHub API）：仅 `17.5-00-example.py` 与 `17.5-01-tree-to-list.py` | 17→18 唯一真实 codemod = `17.5-01-tree-to-list` |
| 版本号 | `odoo/release.py`：`version_info = (18, 0, 0, FINAL, 0, '')` | 18.0 |

> 注：`odoo/models.py` 在抓取时被截断（标注 `[content truncated]`），"REMOVED" 结论以官方 changelog + OCA 交叉为强证；`copy_data` 等方法的"移除"系截断噪音，`copy_data` 在 18.0 仍存在（仅语义变多记录），勿误读。

## 三、社区来源（交叉核实）

- **OCA `maintainer-tools`《Migration to version 18.0》**：`tree`→`list`（PR #159909）、`user_has_groups`→`env.user.has_group`（#151597）、`check_access_rights`/`check_access_rule`→`check_access`、`_filter_access_rules*`→`_filtered_access`（#179148）、`_name_search`→`_search_display_name`、`check_recursion`→`has_cycle`、`group_operator`→`aggregator`、`copy`/`copy_data` 多记录、非存储 related 字段搜索抛异常（改用 `search_fetch`）、缺失字段自动补、`tree_view_ref`→`list_view_ref`、`kanban-box`→`card`、资产/SCSS 变化。
- **Cybrosys《Odoo 18 v/s Odoo 17》**：`check_access`/`has_access`/`_filtered_access`、`env._()` 翻译、`inselect`→`in`、`aggregator`、日期粒度、`_flush_search` 弃用、`type='json'`→`jsonrpc`、`rpc` 替代 `jsonrpc` JS。
- **ODIWARE《17 to 18 Migration Guide》**：`name_get` 移除、`tree`→`list` 三处位置、第三方应用阻塞、升级紧迫性。
- **DeployMonkey《Odoo 18 Breaking Changes》**：`states` 字段属性移除、`fields_view_get`→`get_views`、资产/SCSS 重构、PG 14+、Longpolling→WebSocket、前端 Owl 3（`[verify]`：前端 Owl 3 之说与官方 18= Owl 2 矛盾，疑误，已按官方结论处理）。

## 四、版本作用域纪律（17→18）

- **纳入**：首次出现于 `∈ [17.0, 18.x]` 的改动（含 17.1–17.4 Online 与 18.0–18.2 Online）。对从 17 出发的迁移均为"新增"。
- **排除（属更晚版本）**：Owl 3 / ORM 包拆分 / `web_editor` 拆分 / `res.groups` privilege 模型 / `ir.access.csv` —— 均归 18→19 或 19→20，由对应技能处理（见根 `README.md` 矩阵）。
- **PG 地板 / kanban-box 版本归属 / states / fields_view_get / 资产-SCSS**：标 `[verify]`，单一社区来源，待 18.0 源码最终确认。

## 五、修订核实入口

- **CE 差异**：`github.com/odoo/odoo` 分支 `17.0` vs `18.0`（grep 模型/字段/方法名）。
- **EE 差异**：Enterprise 18.0 树。
- **codemod 清单**：`odoo/upgrade_code/`——17→18 仅 `17.5-01-tree-to-list`（前缀 `17.5` 即落在 17→18 区间）。
- **一致性校验**：修订后跑 `python3 work/17to18/check_cookbook_consistency.py`，确保 Cookbook 与 Skill references 不漂移。
