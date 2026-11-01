# 5→6 模块 / 清单 / 结构 映射表（源码核对版）

> 来源：OpenERP 5.0 官方文档（doc.odoo.com/5.0）+ 社区 `__openerp__.py` 演进说明 + 6.0 发布说明。
> 作用域：仅 5→6。**模型层无大规模重命名**（`res.partner.address`→拆分 属 6→7；`account.invoice`→`account.move` 属 12→13）。

## 1. 清单文件名改名  — CONFIRMED

| 5.0 | 6.0 | 备注 |
|---|---|---|
| `__terp__.py` | `__openerp__.py` | 清单文件名改名；6.0 仍兼容旧名但新代码应改名 |

- 把模块根目录的 `__terp__.py` 重命名为 `__openerp__.py`。
- 扫描 id：`terp-manifest`（正则 `__terp__\.py`）。

## 2. 清单键重映射  — CONFIRMED

| 5.0 键 | 6.0 键 | 备注 |
|---|---|---|
| `init_xml` | `data` | 安装时加载的 XML |
| `update_xml` | `data` | 安装/更新均加载的 XML（并入 `data`） |
| `demo_xml` | `demo` | 演示数据 |
| （无） | `test` | 6.0 新增：测试数据键 |
| （无） | `web` | 6.0 新增：web 客户端资源标记（布尔，[verify]） |

- `init_xml` 与 `update_xml` 合并为 `data`；`demo_xml` 改名为 `demo`。
- 扫描 id：`manifest-keys`（正则 `'init_xml'|'update_xml'|'demo_xml'`）。

## 3. 模块结构（目录约定）  — CONFIRMED（结构指引）

| 目录 | 用途 | 备注 |
|---|---|---|
| `report/` | 报表文件（RML / 新版报表） | 6.0 推荐归位 |
| `static/` | web 客户端静态资产（JS/CSS/图片） | 配合 6.0 默认 web client |

- 这两个目录是**结构指引**而非强制破坏性变更；具体子路径（如 `static/src/js`）在 6.0 尚不成熟（[verify]）。

## 4. manifest 小结

- 整个 `manifest` 文件从 `__terp__.py` 改名为 `__openerp__.py`，键集合从
  `init_xml`/`update_xml`/`demo_xml` 演进为 `data`/`demo`/`test`/`web`。
- 本卷**只**覆盖这一步；`__openerp__.py`→`__manifest__.py` 属 9→10，勿顺手继续改名。

## 5. 红线

- `__openerp__.py`→`__manifest__.py` → 9→10；`openerp`→`odoo` 包改名 → 9→10；
- `osv.osv`→`osv.Model` 基类改名 → 6→7；`res.partner.address` 移除 → 6→7；
- `@api.*` 新 API / `self.env` / `fields.Date` 对象 → 7→8 / 11→12；
- `account.invoice`→`account.move` → 12→13。
