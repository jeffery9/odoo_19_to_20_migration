# 11→12 `upgrade_code` codemod 清单（11→12 无 codemod）

> 来源：odoo/odoo 仓库 `odoo/upgrade_code/` 目录在 16.0 / 17.0 / 18.0 的核查结论——
> 该 codemod 引擎**仅在 18.0+ 存在**（17.0 及更早均无此模块）。已对 12.0 分支核实：无 `upgrade_code`。
> 作用域：明确"11→12 零 codemod"，所有修复均手工 + 数据库级 `migrations/12.0/`。

## 1. 事实

- `odoo-bin upgrade_code` 命令依赖 `odoo/upgrade_code/` 模块；该模块在 **18.0** 首次出现。
- 12.0 分支**不存在** `odoo/upgrade_code/` → 11→12 **零 codemod**。
- 对比：17→18 有 1 个（`17.5-01-tree-to-list`），18→19 有多个；11→12 / 12→13 / 13→14 / 14→15 均为零。

## 2. 对 11→12 迁移的实操含义

- ⚠️ **勿让用户跑 `odoo-bin upgrade_code --from 11.0`**——12.0 安装中该命令不存在，会报命令未找到。
- 所有 11→12 断裂（`@api.one`、`from_string`、`act_window.view`、`do_notify`、`t-field-options`、
  `parent_left/right`）均为**手工**改动，由 `Odoo11to12Migration/references/*` 映射表承接。
- 数据库级变更（如 `parent_path` 填充）写模块内 `migrations/12.0/` 脚本，由 OpenUpgrade 框架执行。

## 3. 工作流

1. **Scan**：`python3 scripts/scan_addon.py /path/to/addons` —— 列出所有 11-only API 命中。
2. **手工修复**：按 `references/*` 映射逐条改（api.one→循环、from_string→to_date、act_window.view→view_ids 等）。
3. **DB 迁移**：模块 `migrations/12.0/` 写数据脚本（`parent_path` 填充等）。
4. **校验**：`odoo-bin -u <module> --test-tags /<module>`，`--dev=all` 清除 `DeprecationWarning`（`api.one` 警告等）。
5. **复扫**：重跑 scanner 期望结果为 0；出报告。
