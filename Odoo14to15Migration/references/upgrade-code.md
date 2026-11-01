# 14→15 `upgrade_code` codemod 清单（14→15 无 codemod）

> 来源：odoo/odoo 仓库 `odoo/upgrade_code/` 目录核查 —— 该 codemod 引擎**仅在 18.0+ 存在**
> （17.0 及更早均无此模块）。已对 15.0 分支核实：无 `upgrade_code`。
> 作用域：明确"14→15 零 codemod"，所有修复均手工 + 数据库级 `migrations/15.0/`。

## 1. 事实

- `odoo-bin upgrade_code` 命令依赖 `odoo/upgrade_code/`；该模块在 **18.0** 首次出现。
- 15.0 分支**不存在** `odoo/upgrade_code/` → 14→15 **零 codemod**。
- 对比：17→18 有 1 个、18→19 有多个；11→12 / 12→13 / 13→14 / 14→15 均为零。

## 2. HTTP / 邮件（14→15 变化与不变）

- **变化**：邮件模板 Jinja→QWeb/inline_template、subtype→subtype_xmlid（见 http-rpc-mail.md）。
- **不变**：`http.route`/`request.env`/`message_post`/`get_resource_path` 行为一致。

## 3. 对 14→15 迁移的实操含义

- ⚠️ **勿让用户跑 `odoo-bin upgrade_code --from 14.0`**——15.0 安装中该命令不存在，会报命令未找到。
- 所有 14→15 断裂（`t-raw`→`t-out`/`t-esc`、`ir.model*` 访问、`@odoo-module`→`.esm.js`、资产进 manifest、
  `SavepointCase`→`TransactionCase`、`Environment.manage` 移除、Jinja→QWeb 邮件）均为**手工**改动，
  由 `Odoo14to15Migration/references/*` 映射表承接。
- 数据库级变更写模块内 `migrations/15.0/` 脚本，由 OpenUpgrade 框架执行。

## 4. 工作流

1. **Scan**：`python3 scripts/scan_addon.py /path/to/addons` —— 列出所有 14-only / 15-breaking API 命中。
2. **手工修复**：按 `references/*` 映射逐条改（t-raw→t-out/esc、ir.model*→sudo、esm.js、manifest assets 等）。
3. **DB 迁移**：模块 `migrations/15.0/` 写数据脚本（如需）。
4. **校验**：`odoo-bin -u <module> --test-tags /<module>`，`--dev=all` 清除 `DeprecationWarning`。
5. **复扫**：重跑 scanner 期望结果为 0；出报告。
