# 12→13 `upgrade_code` codemod 清单（12→13 无 codemod）

> 来源：odoo/odoo 仓库 `odoo/upgrade_code/` 目录核查 —— 该 codemod 引擎**仅在 18.0+ 存在**
> （17.0 及更早均无此模块）。已对 13.0 分支核实：无 `upgrade_code`。
> 作用域：明确"12→13 零 codemod"，所有修复均手工 + 数据库级 `migrations/13.0/`。

## 1. 事实

- `odoo-bin upgrade_code` 命令依赖 `odoo/upgrade_code/`；该模块在 **18.0** 首次出现。
- 13.0 分支**不存在** `odoo/upgrade_code/` → 12→13 **零 codemod**。
- 对比：17→18 有 1 个、18→19 有多个；11→12 / 12→13 / 13→14 / 14→15 均为零。

## 2. HTTP / 邮件 / 二进制（12→13 不变）  — CONFIRMED

- `http.route`、`request.env`、`http.Controller` 在 12/13 一致；`type='json'` 仍是 `json`
  （重命名为 `jsonrpc` 是 **18.1**）。
- 邮件 `mail.template`：`body_html` 仍用 **Jinja** 语法（Jinja→QWeb 重写是 **14→15**）；
  `subtype` → `subtype_xmlid` 改名也是 **14→15**。
- `message_post(body=..., message_type=...)` 行为一致。
- `get_resource_path` 在 12/13 仍使用（`file_path` 是 **16→17** 改名）。

## 3. 对 12→13 迁移的实操含义

- ⚠️ **勿让用户跑 `odoo-bin upgrade_code --from 12.0`**——13.0 安装中该命令不存在，会报命令未找到。
- 所有 12→13 断裂（account.move、`@api.multi`、`dp.get_precision`、`track_visibility`、`oldname`、
  `src_model`、`binding_view_types`、computed 赋值、`with_user`、`.env.company`）均为**手工**改动，
  由 `Odoo12to13Migration/references/*` 映射表承接。
- 数据库级变更（account.move 数据搬移、`oldname` 重命名字段、Binary 附件落库）写模块内
  `migrations/13.0/` 脚本，由 OpenUpgrade 框架执行。

## 4. 工作流

1. **Scan**：`python3 scripts/scan_addon.py /path/to/addons` —— 列出所有 12-only / 13-breaking API 命中。
2. **手工修复**：按 `references/*` 映射逐条改（account.move、`@api.multi`→去装饰器、`dp.get_precision`→`digits` 等）。
3. **DB 迁移**：模块 `migrations/13.0/` 写数据脚本。
4. **校验**：`odoo-bin -u <module> --test-tags /<module>`，`--dev=all` 清除 `DeprecationWarning`。
5. **复扫**：重跑 scanner 期望结果为 0；出报告。
