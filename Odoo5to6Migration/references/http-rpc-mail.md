# 5→6 HTTP / RPC / 邮件 / 二进制 映射表（源码核对版）

> 来源：OpenERP 5.0/6.0 源码核对 + 官方 RPC 文档。
> 作用域：仅 5→6。本卷区间这些子系统**基本不变**。

## 1. HTTP / 控制器  — CONFIRMED（基本不变）

- 5.0/6.0 仍使用 `openerp` 包下的服务暴露（netrpc / xmlrpc）；6.0 的 web
  client 带来新的 HTTP 入口，但自定义模块的控制/接口形态基本延续。
- 具体 6.0 `openerp.service` / web 控制器的暴露差异属 [verify]，以 6.0 源码为准。

## 2. 邮件 / 模板  — CONFIRMED（基本不变）

- 5.0/6.0 的 `email_template` 与 `mail` 雏形尚不成熟；模板与 `res.partner`
  邮件字段基本延续 5.0 形态。
- Jinja/Python-format 邮件渲染移除发生在 14→15，不属本卷。

## 3. 二进制字段  — CONFIRMED（不变）

- `fields.binary` 用法在 5→6 不变（默认存库字段）；存 `ir.attachment` 的时机远在 13.0。

## 4. web client 关联

- 6.0 的 web client（见 views-qweb.md 第 1 节）是此区间最大的"前端"变化；
  但控制器/RPC 接口本身基本不变（[verify]-light）。

## 5. 红线

- `t-raw` / Jinja 邮件渲染 → 14→15；
- `openerp.http`→`odoo.http` 改名属 9→10；
- 控制器大改不属 5→6。
