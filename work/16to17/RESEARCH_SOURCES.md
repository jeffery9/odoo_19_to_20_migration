# 16→17 研究来源查证地图（work/16to17）

本文件记录 16→17 每一条破坏性变更的**来源与核实状态**，供后续修订/复核复用。
核查日期：2026-11-01。符号：`C`=CONFIRMED（源码/官方多源）、`V`=[verify]（单一/分歧源）、`E`=[EE-verify]。

## A. 源码核实（GitHub `odoo/odoo` 17.0 分支）

| 变更 | 17.0 源码证据 | 状态 |
|---|---|---|
| `attrs`/`states` 硬拒 | `odoo/addons/base/models/ir_ui_view.py`：`_check_xml` 抛 `ValidationError(_('Since 17.0, the "attrs" and "states" attributes are no longer used.'))`（xpath `//*[@attrs]` / `//*[@states]`） | C |
| `<tree>` 在 17.0 仍合法 | 同上文件 `type` 选单含 `('tree','Tree')`（非仅 `list`） | C |
| `get_resource_path` 移除 / `file_path` 存在 | `odoo/tools/misc.py`：无 `def get_resource_path`；有 `def file_path(file_path, filter_ext=('',), env=None)` | C |
| Python 版本地板 | `odoo/release.py`：`version_info = (17,0,0,FINAL,0,'')` | C |
| 依赖下限 | `odoo/requirements.txt`：`libsass==0.20.1/0.22.0`（SCSS 仍编译）、`Werkzeug==2.0.2/2.2.2/3.0.1`、`psycopg2==2.9.2`、`passlib==1.7.4`、`PyPDF2` | C |
| **无 `upgrade_code` codemod** | `odoo/upgrade_code/` 目录列举 404；`odoo/upgrade_code/__init__.py` 404 | C |
| `mail_thread.py` 路径变更 | 18 风格 `odoo/addons/mail/models/mail_thread.py` 在 17.0 返回 404（目录结构调整，不影响行为结论） | C（路径） |

## B. OCA `maintainer-tools`《Migration to version 17.0》（框架清单）

| 变更 | PR / commit |
|---|---|
| `attrs`/`states` → 内联表达式 | PR #104741 |
| `res.config.settings` 简化（`<app>`/`<block>`/删 pane） | PR #106425 |
| `name_get` → `_compute_display_name` | PR #122085（16.4 弃用） |
| 钩子 `(cr, registry)` → `env` | commit b4a7996 |
| `get_resource_path` → `file_path` | PR #135607 |
| `active_id`/`active_ids`/`active_model` context → `id`/硬编码 | commit daf05d48 |
| 列表 `invisible="1"` → `column_invisible="1"` | OCA 17 指南 |
| Python 3.10+ | OCA 17 指南 |

## C. 社区交叉核实

| 来源 | 提供/确认 | 状态 |
|---|---|---|
| odoohub《第二章 odoo 版本差异》 | `message_post` body 默认文本/Markdown（HTML 需 `body_is_html`）；`states` 属性取消；Python 3.10；`mail.channel→discuss.channel` 归属澄清（实为 18.0） | C（与 OCA 一致） |
| Medium《Odoo Migration Decoded 16→17→18→19》 | `message_post`/`Markup`；`t-raw`→`t-out`（属 19）；SCSS libsass→dart-sass 说法——**与 requirements.txt 冲突，以源码为准纠偏** | 部分 V |
| LobeHub frontend skill | Bootstrap 4→5 类名映射；但版本归属存在分歧（一称 16+，一称 jQuery 在 17 仍可用、Bootstrap 5.1.3 归 18/19） | V |
| oec.sh 需求页 | PostgreSQL 12+、Python 3.10+ | V（PG 下限待 sql_db.py 确认） |

## D. 已纠偏的误传

- **"Odoo 17 移除 SCSS 编译"** → 误。17.0 `requirements.txt` 仍含 `libsass`，SCSS 仍编译；该移除属 post-17.0 版本。已在烹饪书第 1.2 章显式标注。
- **"Bootstrap 5 / jQuery 移除属 16→17"** → 来源间分歧，官方 17 发布说明未提及；标 `[verify]`，要求以 17.0 实机 `web.assets_frontend` 为准。
- **`mail.channel`→`discuss.channel` 属 17.0** → 误（odoohub 混合列表误导）。17.0 仍 `mail.channel`，重命名在 18.0。已排除出 16→17 作用域。

## E. 版本作用域红线（16→17 不处理，归后续技能）

`tree`→`list`（17→18）、`name_get`/`check_access_rights`/`user_has_groups`/`check_recursion`/`inselect` **移除**（17→18）、`aggregator` 改名（17.2，17→18 的 Online 面）、`type='json'`→`jsonrpc`（18.1）、`res.groups`/`ir.access.csv`（19→20）、`web_editor` 拆分（19.0）、Owl 3（19.0）。
