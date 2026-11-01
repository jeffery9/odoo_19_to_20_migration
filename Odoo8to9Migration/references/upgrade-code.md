# 8→9 upgrade_code codemod 状态（源码核对版）

> 来源：`odoo/upgrade_code/` / `openerp/upgrade_code/` 引擎可用性核对（odoo 仓库）。
> 结论：**8→9 无任何 `upgrade_code` codemod。**

## 1. codemod 引擎可用性  — CONFIRMED

- `odoo-bin upgrade_code` 引擎自 **18.0** 才随官方发布；8.0 / 9.0 源码树中**不存在** `odoo/upgrade_code/` 或 `openerp/upgrade_code/` 模块。
- 因此 8→9 的全部代码迁移（异常替换、`ir.model` 字段/方法改名、`osv_memory_autovacuum`→`ir_autovacuum`、Enterprise 依赖审计）均为**手工**映射，无自动重写脚本。

## 2. 数据迁移职责

- 数据库级结构变更（字段/模型/Enterprise 模块拆分）由 **OpenUpgrade**（社区）或官方升级服务处理。
- 自定义模块只需提供 **代码级** 映射（本技能 `references/*` 表）+ 必要的 `migrations/9.0/` 数据脚本（如 Enterprise 依赖审计、字段 `osv_memory`→`transient` 的历史数据处理）。

## 3. 迁移命令（参考）

```bash
# 代码扫描（无 codemod，全部 manual）
python3 scripts/scan_addon.py /path/to/addons

# 数据迁移脚本放置
my_module/migrations/9.0/pre-_audit_enterprise_deps.py
```

## 4. 红线

- 切勿提示用户运行 `openerp-bin upgrade_code --from 8.0`；该命令在 9.0 不存在。
- `upgrade_code` 可用的最早目标版本为 18.0；9→10 / 10→11 / … / 17→18 同样无 codemod。
