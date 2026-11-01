# 10→11 upgrade_code codemod 状态（源码核对版）

> 来源：`odoo/upgrade_code/` 引擎可用性核对（OCA/odoo 仓库）。
> 结论：**10→11 无任何 `upgrade_code` codemod。**

## 1. codemod 引擎可用性  — CONFIRMED

- `odoo-bin upgrade_code` 引擎自 **18.0** 才随官方发布；10.0/11.0 源码树中**不存在** `odoo/upgrade_code/` 模块。
- 因此 10→11 的全部代码迁移（Python 3 改写、Workflow→方法、报表 API、模块改名）均为**手工映射**，无自动重写脚本。

## 2. 数据迁移职责

- 数据库级结构变更（字段/模型/工作流表清理）由 **OpenUpgrade**（社区）或官方升级服务处理。
- 自定义模块只需提供 **代码级** 映射（本技能 `references/*` 表）+ 必要的 `migrations/11.0/` 数据脚本（如工作流残留数据清理）。

## 3. 迁移命令（参考）

```bash
# 代码扫描（无 codemod，全部 manual）
python3 scripts/scan_addon.py /path/to/addons

# 数据迁移脚本放置
my_module/migrations/11.0/pre-_clean_workflow.py
```

## 4. 红线

- 切勿提示用户运行 `odoo-bin upgrade_code --from 10.0`；该命令在 11.0 不存在。
- `upgrade_code` 可用的最早目标版本为 18.0；11→12/12→13/…/17→18 同样无 codemod。
