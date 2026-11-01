# 14→15 HTTP / RPC / 邮件 / 二进制映射表（源码核对版）

> 来源：`OCA Migration to version 15.0` 官方指南 + odoo/odoo#77074。
> 作用域：仅指出 14→15 的邮件模板变化（Jinja→QWeb）+ 其它不变的边界，避免误改。

## 1. 邮件模板 Jinja → QWeb / inline_template  — CONFIRMED

- 15.0：`mail.template` 渲染从 Jinja 改为两种语言：
  - 正文 `body_html`：用 **QWeb**（加 `type="qweb"`），支持 `t-out`/`t-esc`。
  - `subject` / `email_from` / `email_to` 等：用 **inline_template**，表达式包在 `{{ }}`（替代旧的 `${ }`）。
- 扫描 id：`jinja-dollar`（正则 `\$\{` 捕捉旧 Jinja）、`mail-qweb`（正文 `type="qweb"`）。
- 源码：odoo/odoo#77074。

## 2. `subtype` → `subtype_xmlid`（[verify]）

- 15.0 邮件 `message_post` / `mail.template` 的 `subtype` 字段改为 `subtype_xmlid`（引用 xml-id）。
- OCA 15.0 核心指南未逐条列；社区普遍归入 14→15，建议 15.0 源码核对。
- 扫描 id：`subtype-xmlid`（正则 `subtype=` 邮件上下文）。

## 3. HTTP / 控制器（不变）  — CONFIRMED

- `@http.route`、`http.Controller`、`request.env` 在 14/15 一致；`type='json'` 仍是 `json`
  （重命名 `jsonrpc` 是 **18.1**）。

## 4. 二进制 / 资源路径（不变）  — CONFIRMED

- `get_resource_path` 在 14/15 仍使用（重命名 `file_path` 是 **16→17**）。
- `Binary` 字段默认存储行为 14/15 一致（默认存 `ir.attachment` 自 **13.0** 起）。

## 5. 红线（勿套用更晚版本）

- `message_post(body_is_html=...)` → 16→17
- `get_resource_path` → `file_path` → 16→17
- `t-raw` 移除 / `ir.model*` 移除 / 资产进 manifest → 14→15（本版本对即处理）
