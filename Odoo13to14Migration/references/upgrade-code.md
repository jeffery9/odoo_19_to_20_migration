# 13→14 `upgrade_code` codemod 清单（13→14 无 codemod）

> 来源：odoo/odoo 仓库 `odoo/upgrade_code/` 目录核查 —— 该 codemod 引擎**仅在 18.0+ 存在**
> （17.0 及更早均无此模块）。已对 14.0 分支核实：无 `upgrade_code`。
> 作用域：明确"13→14 零 codemod"，所有修复均手工 + 数据库级 `migrations/14.0/`。

## 1. 事实

- `odoo-bin upgrade_code` 命令依赖 `odoo/upgrade_code/`；该模块在 **18.0** 首次出现。
- 14.0 分支**不存在** `odoo/upgrade_code/` → 13→14 **零 codemod**。
- 对比：17→18 有 1 个、18→19 有多个；11→12 / 12→13 / 13→14 / 14→15 均为零。

## 2. 对 13→14 迁移的实操含义

- ⚠️ **勿让用户跑 `odoo-bin upgrade_code --from 13.0`**——14.0 安装中该命令不存在，会报命令未找到。
- 所有 13→14 断裂（`ir.actions.*` 访问、invisible/readonly 动态表达式、_name_search 返回 ids、
  name_get、`force_company`、`Char` size、`selection_add` ondelete、TransientModel ACL）均为**手工**改动，
  由 `Odoo13to14Migration/references/*` 映射表承接。
- 数据库级变更（selection 选项迁移等）写模块内 `migrations/14.0/` 脚本，由 OpenUpgrade 框架执行。

## 3. 工作流

1. **Scan**：`python3 scripts/scan_addon.py /path/to/addons` —— 列出所有 13-only / 14-breaking API 命中。
2. **手工修复**：按 `references/*` 映射逐条改（ir.actions.*→_for_xml_id、invisible→attrs 等）。
3. **DB 迁移**：模块 `migrations/14.0/` 写数据脚本。
4. **校验**：`odoo-bin -u <module> --test-tags /<module>`，`--dev=all` 清除 `DeprecationWarning`
   （视图加载会校验 invisible/readonly 合法性）。
5. **复扫**：重跑 scanner 期望结果为 0；出报告。
