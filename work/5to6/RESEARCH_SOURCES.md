# 5→6 研究来源与溯源（RESEARCH_SOURCES）

> 本文件记录 OpenERP 5.0 → 6.0 每一处破坏性变更的取证来源与可信度层级。
> 配对非常古老（2010–2011），官方文档多已离线，故大量框架级断言标注 [verify]。

## 一、CONFIRMED 锚点事实（双源互证）

| 变更 | 来源 | 备注 |
|---|---|---|
| 清单文件名 `__terp__.py` → `__openerp__.py` | OpenERP 5.0 官方文档（doc.odoo.com/5.0）展示 `__terp__.py` 形态；社区 `__openerp__.py` 演进文档确认 6.0 改名 | 双源互证，CONFIRMED |
| 清单键 `init_xml`/`update_xml`→`data`、`demo_xml`→`demo` | 同上：5.0 文档列 `init_xml`/`demo_xml`/`update_xml`；6.0 引入 `data`/`demo`/`test`/`web` | 双源互证，CONFIRMED |

## 二、[verify] 社区/单源项

| 变更 | 来源 | 风险 |
|---|---|---|
| 6.0 引入新默认 web client（GTK 仍可用） | OpenERP 6.0 发布说明 + 社区经验 | [verify]-light：文档零散 |
| `report/` 与 `static/` 模块目录约定 | 6.0 发布说明 + 社区实践 | [verify]：子路径在 6.0 不成熟 |
| `test` / `web` 清单键的加载时机 | 社区文档 | [verify]：以 6.0 源码 `openerp/modules/loading.py` 为准 |
| 5→6 视图 widget 差异 | [verify] | 以 6.0 源码 `addons/base/` 为准 |

## 三、CE / EE 验证入口

- 本卷为 CE（OpenERP 5.0/6.0 社区版）。无 Enterprise-only 项需 [EE-verify]。
- 最终核对基准：6.0 源码树 `openerp/modules/`（`__terp__.py`/`__openerp__.py` 加载）、
  `openerp/osv/osv.py`（ORM 基类）、`addons/web`（早期 web client）。

## 四、被排除的"更晚版本"项（红线来源）

- OCA 版本迁移指南 + Odoo 版本变更史确认：
  - `osv.osv`→`osv.Model`、res.partner.address 移除 → 6→7；
  - `__openerp__.py`→`__manifest__.py`、`openerp`→`odoo` → 9→10；
  - `@api.*`/`self.env`/`fields.Date` 对象 → 7→8 / 11→12；
  - `account.invoice`→`account.move` → 12→13。
