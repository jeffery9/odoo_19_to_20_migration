# 14→15 HTTP / RPC / 邮件 / 二进制映射表（源码核对版）

> 来源：Odoo CE 14.0 / 15.0 源码树复核（`mail_render_mixin.py`、`mail_template.py`、`mail_thread.py`）。
> 作用域：本版本对真正变化的邮件渲染，+ 其它「不变」的边界（避免误改）。

## 1. 邮件模板 Jinja → QWeb / inline_template  — CONFIRMED

- 14.0：`_render_template(..., engine='jinja')` 为默认，Body 是普通 Html 字段。
- 15.0：
  - 默认 engine 变为 `inline_template`；允许值 `inline_template`、`qweb`、`qweb_view`；
    传 `engine='jinja'` **抛 `ValueError`**（`_render_template_jinja` 等方法已不存在）。
  - 正文 `body_html` 字段定义加了 `render_engine='qweb'`，即正文以 QWeb 渲染。
  - `subject` / `email_from` / `email_to` 用 **inline_template**，表达式包在 `{{ }}`（替代旧的 `${ }`）。
- **数据 XML 里没有 `type="qweb"` 这种写法**（15.0 全库 XML 零出现，写了会报错）。
  正文用 `type="html"`；14.0 里少量 `type="xml"` 的 body 在 15.0 也统一为 `type="html"`。
- 批量迁移存量模板可用 `convert_inline_template_to_qweb()`（`odoo.tools.rendering_tools`）。
- 扫描 id：`jinja-dollar`（正则 `\$\{`）、`engine-jinja`（正则 `engine\s*=\s*['"]jinja`）。
- 源码：odoo/odoo#77074。

## 2. `subtype` → `subtype_xmlid`：**不属本版本对**（属 13→14）

`mail_thread.message_post` 的签名演变（源码实测）：

| 版本 | 参数 |
|---|---|
| 11.0 / 12.0 | `subtype=None` |
| 13.0 | `subtype_id=False, subtype=None`（过渡，新旧并存） |
| 14.0 / 15.0 | `subtype_xmlid=None, subtype_id=False` |

14.0 与 15.0 完全一致，因此**14→15 不需要改**。若代码里仍有 `subtype=`，说明模块没真正迁到 14.0，
应回 13→14 处理。扫描器不再报此项。

## 3. HTTP / 控制器（不变）  — CONFIRMED

- `@http.route`、`http.Controller`、`request.env` 在 14/15 一致；`type='json'` 仍是 `json`
  （重命名 `jsonrpc` 是 **18.1**）。

## 4. 二进制 / 资源路径（不变）  — CONFIRMED

- `get_resource_path` 在 14/15 仍使用（重命名 `file_path` 是 **16→17**）。
- `Binary` 字段默认存储行为 14/15 一致（默认存 `ir.attachment` 自 **13.0** 起）。

## 5. 红线（勿套用更晚版本）

- `message_post(body_is_html=...)` → 16→17
- `get_resource_path` → `file_path` → 16→17
- `t-raw` 的**彻底移除** → **15→16**（15.0 仅弃用）
- `subtype`→`subtype_xmlid` → **13→14**（本对不涉及）
- 「15.0 移除 `ir.model*` 访问」不成立（详见 orm-api.md）
