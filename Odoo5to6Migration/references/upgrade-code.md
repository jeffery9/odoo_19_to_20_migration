# 5→6 upgrade_code codemod 状态（源码核对版）

> 来源：`odoo/upgrade_code/` 引擎可用性核对（OCA/odoo 仓库）。
> 结论：**5→6 及更早版本无任何 `upgrade_code` codemod。**

## 1. codemod 引擎可用性  — CONFIRMED

- `odoo-bin upgrade_code` 引擎自 **18.0** 才随官方发布；6.0 源码树（乃至整个
  `odoo` 包，因为 6.0 仍是 `openerp` 包）中**不存在** `upgrade_code` 模块。
- 因此 5→6 的全部代码迁移（清单文件名改名、清单键重映射、目录整理）均为
  **手工映射**，无自动重写脚本。

## 2. 数据迁移职责

- 数据库级结构变更（字段/模型结构）由 **OpenUpgrade**（社区）或官方升级服务处理。
- 自定义模块只需提供 **代码级** 映射（本技能 `references/*` 表）+ 必要的
  `migrations/6.0/` 数据脚本。

## 3. 迁移命令（参考）

```bash
# 代码扫描（无 codemod，全部 manual）
python3 scripts/scan_addon.py /path/to/addons

# 数据迁移脚本放置
my_module/migrations/6.0/pre-_fix_manifest.py
```

## 4. 红线

- 切勿提示用户运行 `openerp-server upgrade_code --from 5.0`；该命令在 6.0 不存在。
- `upgrade_code` 可用的最早目标版本为 18.0；6→7/7→8/…/17→18 同样无 codemod。
- 本卷的 `manifest` 文件（`__terp__.py`→`__openerp__.py`）与键重映射
  （`init_xml`/`update_xml`/`demo_xml`→`data`/`demo`/`test`）均为手工，不由
  OpenUpgrade 的 `upgrade_code` 引擎处理。
