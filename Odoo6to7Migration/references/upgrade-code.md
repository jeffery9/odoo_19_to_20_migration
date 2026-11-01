# 6→7 `upgrade_code` codemod 清单（6→7 无 codemod）

> 来源：odoo/odoo 仓库 `odoo/upgrade_code/` 目录核查结论——
> 该 codemod 引擎**仅在 18.0+ 存在**（17.0 及更早均无此模块）。已对 7.0 分支核实：无 `upgrade_code`。
> 作用域：明确"6→7 零 codemod"，所有修复均手工 + 数据库级 `migrations/7.0/`（OpenUpgrade）。

## 1. 事实

- `odoo-bin upgrade_code` 命令依赖 `odoo/upgrade_code/` 模块；该模块在 **18.0** 首次出现。
- 7.0 分支**不存在** `odoo/upgrade_code/` → 6→7 **零 codemod**。
- 对比：17→18 有 1 个（`17.5-01-tree-to-list`），18→19 有多个；6→7 / 7→8 / … / 16→17 均为零。

## 2. 对 6→7 迁移的实操含义

- ⚠️ **勿让用户跑 `odoo-bin upgrade_code --from 6.0`**——7.0 安装中该命令不存在，会报命令未找到。
- 所有 6→7 断裂（`osv.osv`→`osv.Model`、`res.partner.address` 合并、`update_xml`→`data`、`version="7.0"`/`sheet`）均为**手工**改动，由 `Odoo6to7Migration/references/*` 映射表承接。
- 数据库级变更（如 `res_partner_address` 并入 `res.partner`、字段结构）写模块内 `migrations/7.0/` 脚本，由 **OpenUpgrade** 框架执行。

## 3. 工作流

1. **Scan**：`python3 scripts/scan_addon.py /path/to/addons` —— 列出所有 6-only API 命中。
2. **手工修复**：按 `references/*` 映射逐条改（`osv.osv`→`osv.Model`、`res.partner.address`→`res.partner` 字段、`update_xml`→`data`、视图 `version="7.0"`/`sheet`）。
3. **DB 迁移**：模块 `migrations/7.0/` 写数据脚本（地址字段并入 `res.partner` 等）。
4. **校验**：`openerp-server -u <module> --test-enable`，清除 `DeprecationWarning`（`osv.osv` 弃用警告等）。
5. **复扫**：重跑 scanner 期望结果为 0；出报告。
