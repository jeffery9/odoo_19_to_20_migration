# 6→7 研究来源与源码核实地图

> 本文件记录 6→7 每条破坏性变更的溯源与核实状态，供修订时复核。

## 已核实（CONFIRMED）

| 变更 | 来源 | 核实方式 |
|---|---|---|
| OpenERP 7.0（2012-12）"not just an update"，新 Web 客户端 + Bootstrap | OpenERP 7.0 Release Notes | 官方发布说明 |
| `osv.osv` → `osv.Model`，`osv.osv_memory` → `osv.TransientModel`，`osv` 成为弃用别名 | 7.0 源码 `openerp.osv` + 论坛 v6→v7 | `openerp.osv.osv` 仍存在但弃用；推荐 `osv.Model` |
| `res.partner.address` 模型移除，地址字段合并进 `res.partner` | 7.0 Release Notes + 论坛 | `res.partner` 含 street/city/email/phone |
| `__openerp__.py` `update_xml`/`init_xml`/`demo_xml` → 统一 `data` 键 | 7.0 源码 manifest 加载 + 论坛 | 7.0 仅识别 `data` 键 |
| 视图 `version="7.0"` + `<sheet>`/`<header>`/`<footer>` + HTML 放开 | dbi-services 6→7 博文 + 7.0 源码 `addons/web` | 新 Web 框架、布局标签 |
| 6/7 使用 `openerp` 包名（非 `odoo`） | 源码核对 | `openerp` 改名 `odoo` 是 9→10 |
| 6→7 仍用旧 API `cr, uid, ids, context`；新 API 7→8 才来 | 源码核对 | `@api.*`/`models.Model`/`self.env` 在 7→8 |
| 7.0 无 `odoo/upgrade_code/` 模块（引擎 18.0 才出现） | odoo/odoo 仓库核查 | codemod 引擎可用性 |

## 待核实（[verify] / [EE-verify]）

| 变更 | 状态 | 备注 |
|---|---|---|
| 前端 Bootstrap 具体大版本号（3.x？） | [verify] | 无权威 6→7 前端清单；以 7.0 源码 `addons/web` 资产为准 |
| EE 专属模块在 7.0 的归属微调 | [EE-verify] | 企业版 7.0 的 module 列表若有调整需对照 EE 树 |

## 版本作用域红线（已对照确认不属于 6→7）

- `openerp`→`odoo` 改名 / `__openerp__.py`→`__manifest__.py` —— **9→10**
- `osv.Model`→`models.Model` / `@api.*` / `self.env` / `osv.except_osv`→`UserError` —— **7→8**
- `@api.one` 移除 / `fields.Date`/`Datetime` 运行时对象化 —— **11→12**
- `res.partner.address` 移除 **属于 6→7**（勿误判为更晚版本）
