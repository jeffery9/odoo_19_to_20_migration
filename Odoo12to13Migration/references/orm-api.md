# 12→13 ORM / 模型 API 映射表（源码核对版）

> 来源：`OCA Migration to version 13.0` 官方指南 + 13.0 源码核对。
> 作用域：仅 12→13。更晚改动（`_name_search` 返回 ids、`ir.actions.*` 访问移除、attrs 硬拒、
> name_get 移除、`ir.model*` 移除）一律不在本表。

## 1. 移除旧装饰器 `@api.multi` / `@api.returns` / `@api.cr` / `@api.model_cr`  — CONFIRMED

- 12.0：`@api.multi`（多记录）、`@api.returns`（返回值转换）、`@api.cr`（游标参数）、
  `@api.model_cr`（模型+游标）仍可用。
- 13.0：以上装饰器**移除**；所有方法默认多记录语义（旧 `api.multi` 行为）。
- 替代：直接去掉装饰器，方法体按 `for rec in self:` 处理；数据库初始化方法直接 `def init(self):`。
- 扫描 id：`api-decorators`（正则 `@api\.(multi|returns|cr|model_cr)`）。

## 2. 非存储 computed 字段必须赋值  — CONFIRMED

- 13.0 要求非存储 computed 字段在 compute 中无论如何都赋值（含 falsy）；存储 computed 字段若未赋值保留旧值。
- 推荐 compute 开头 `self.x = ...` 预赋值。

## 3. `sudo(user)` → `with_user(user)`  — CONFIRMED

- 12.0：`record.sudo(user)` 切换用户。
- 13.0：改用 `record.with_user(user)`；无参 `sudo()` 仍保留。
- 扫描 id：`sudo-user`（正则 `sudo\([^)\s]` 即带参调用）。

## 4. 多公司记录规则新形式  — CONFIRMED

- 旧：`[('company_id','=',False),('company_id','in',company_ids)]`
- 新：`['|',('company_id','=',False),('company_id','in',company_ids)]`
- `noupdate="1"` 记录需补迁移脚本（openupgradelib）。

## 5. `.env.user.company_id` → `.env.company`  — CONFIRMED

- 取"当前激活公司"用 `.env.company`；`env.user.company_id` 在 13.0 已被 `.env.company` 取代。
- 扫描 id：`env-user-company`（正则 `\.user\.company_id`）。

## 6. `hr.employee` → `hr.employee.base`  — CONFIRMED

- 继承 `hr.employee` 的自定义模块改为继承 `hr.employee.base`。

## 7. `with_company()` / `depends_context`  — CONFIRMED

- 13.0 引入 `with_company()` 切换多公司上下文；`depends_context('company')` 用于 computed 字段。
- 注：`with_context(force_company=...)` 在 13.0 仍可用，`force_company` 弃用在 **13→14**。

## 红线（勿套用更晚版本）

- `_name_search` 返回 ids → 13→14；`ir.actions.*` 访问移除（sudo 化）→ 13→14；
- `attrs`/`states` 硬拒 → 16→17；`name_get` 移除 → 17→18；`ir.model*` 移除 → 14→15；
- `SavepointCase`/`Environment.manage` 移除 → 14→15。
