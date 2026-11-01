# 7→8 `upgrade_code` codemod 清单（7→8 无 codemod）

> 来源：odoo/odoo 仓库 `odoo/upgrade_code/` 目录在 16.0 / 17.0 / 18.0 的核查结论——
> 该 codemod 引擎**仅在 18.0+ 存在**（17.0 及更早均无此模块）。已对 8.0 分支核实：无
> `upgrade_code`。作用域：明确"7→8 零 codemod"，所有修复均手工 + 数据库级
> `migrations/8.0/` 由 OpenUpgrade 执行。

## 1. 事实

- `odoo-bin upgrade_code` 命令依赖 `odoo/upgrade_code/` 模块；该模块在 **18.0** 首次出现。
- 8.0 分支**不存在** `odoo/upgrade_code/` → 7→8 **零 codemod**。
- 对比：17→18 有 1 个（`17.5-01-tree-to-list`），18→19 有多个；7→8 / 8→9 / ... / 16→17 均为零。
- 注意 7→8 的 `openerp` 包名在 8.0 仍是 `openerp`（改名到 `odoo` 是 **9→10**），
  因此本对的 codemod 清单中**没有任何包名替换项**。

## 2. 对 7→8 迁移的实操含义

- ⚠️ **勿让用户跑 `odoo-bin upgrade_code --from 7.0`**——8.0 安装中该命令不存在，会报命令未找到。
- 所有 7→8 断裂（new-API 装饰器、 `self.env` 取代 `self.pool`、 `osv.Model`→`models.Model`、
  `osv.except_osv`→`UserError`、 `_columns`→类属性字段、 `qweb-report` 引入）均为**手工**改动，
  由 `Odoo7to8Migration/references/*` 映射表承接。
- 数据库级变更（少量列/结构微调）写模块内 `migrations/8.0/` 脚本，由 **OpenUpgrade** 框架执行。
- 8.0 及更早**没有** `upgrade_code` 自动化引擎；不要假设任何批量重写脚本存在。

## 3. 工作流

1. **Scan**：`python3 scripts/scan_addon.py /path/to/addons` —— 列出所有 7-only API 命中。
2. **手工修复**：按 `references/*` 映射逐条改（加 `@api.*` 装饰器、 `(cr,uid,ids,context)`→recordsets、
   `osv.Model`→`models.Model`、 `osv.except_osv`→`UserError`、 `_columns`→类属性、 RML→QWeb）。
3. **DB 迁移**：模块 `migrations/8.0/` 写数据脚本（极少量结构微调，由 OpenUpgrade 执行）。
4. **校验**：`python3 -m py_compile **/*.py`（catch 语法）， `odoo-bin -u <module> --test-tags /<module>`
   在 8.0 沙箱跑测试；优先清 `ImportError`（`osv` 基类 / `osv.except_osv`） / `AttributeError`（`self.pool`）。
   启动 `--dev=all` 清 `DeprecationWarning`。
5. **复扫**：重跑 scanner 期望结果为 0；出报告。
