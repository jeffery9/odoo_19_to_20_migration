# 14→15 待核实追踪表（VERIFY_TRACKER）

> 修订 SOP：每完成一项核实，把对应行从"待核实"移到下方"已关闭"，并在 `RESEARCH_SOURCES.md`
> 与交付物（`Odoo_Migration_Cookbook_14_to_15.md` + `Odoo14to15Migration/references/*`）同步更新，
> 最后重跑 `check_cookbook_consistency.py` 确保零漂移。

## 待核实（[verify]）

（无。本轮已把此前的 2 项全部关闭，且未新增遗留项。）

## 已关闭（核实后）

| # | 项 | 结论 | 核实依据 |
|---|---|---|---|
| V1 | `subtype` → `subtype_xmlid` 是否属 14→15 | **不属**，实为 **13→14** | `mail_thread.message_post` 签名逐版本对比：11.0/12.0 `subtype=None`；13.0 `subtype_id=False, subtype=None`（过渡）；14.0 与 15.0 均为 `subtype_xmlid=None, subtype_id=False`，两版完全一致 |
| V2 | EE 前端资产细节（EE 15.0 资产分包是否可复用社区版结论） | **可复用** | EE `__manifest__.py` 统计：14.0 `assets`=0 / `qweb`=77；15.0 `assets`=135 / `qweb`=2，与 CE（0/77 → 179/1）同构；EE 15.0 另有 `documents/data/ir_asset.xml` 使用 `ir.asset` |
| V3 | 15.0 是否移除 QWeb `t-raw` | **未移除，仅弃用**（16.0 才移除） | 15.0 `base/models/qweb.py` 保留 `_compile_directive_raw`（warning + 编译为 t-out 语义）；16.0 同文件零 `t-raw` |
| V4 | `t-out` 是否等价旧 `t-raw`（不转义） | **不等价**：`t-out` 默认转义 | 15.0 `qweb.py` `yield str(escape(content))`；`t-raw` 分支额外 `content = Markup(content)` 才保住不转义 |
| V5 | 15.0 是否移除 `ir.model*` 直接访问 | **没有**；真正断裂是 `ir.model.data` 查询 API | `ir_model.py` 14.0↔15.0 diff 无访问控制变更；方法集对比显示 `_get_id(module, xml_id)`/`get_object_reference`/`get_object`/`xmlid_to_object` 移除、`xmlid_*` 加下划线 |
| V6 | `SavepointCase` / `Environment.manage()` 是否移除 | **均未移除**，为弃用（后者 no-op） | 15.0 `odoo/tests/common.py` 定义 `class SavepointCase(TransactionCase)` + 警告，14.0 为 `(SingleTransactionCase)`；15.0 `odoo/api.py` `manage()` 仅 warn + yield |
| V7 | `mail.template` 正文是否需在 XML 写 `type="qweb"` | **无此写法**，引擎由字段参数声明 | 15.0 全库 XML `type="qweb"` 零出现；`mail_template.py` 的 `body_html = fields.Html('Body', render_engine='qweb', ...)` |
| V8 | manifest `qweb` 键在 15.0 是否报错 | **静默忽略**，不报错 | 15.0 `addons/l10n_ae_pos/__manifest__.py` 仍含 `'qweb': [...]` 并可安装；`count` 由 77 降至 1 属官方迁移遗漏 |

## 一致性维护

- 每次修订后运行：`python3 work/14to15/check_cookbook_consistency.py`
- 期望：`CONSISTENCY OK`，所有 token 在 Cookbook↔references 零漂移。
- 任何新引入的 `[verify]` 项必须同时出现在 Cookbook 与至少一个 reference 中。
- 扫描器门禁：`python3 Odoo14to15Migration/scripts/scan_addon.py /path/to/addons` → 修复后期望退出码 0。
- 本轮已移除扫描器的 `subtype-xmlid` 规则（该变更属 13→14），新增 5 条核心模型规则
  （`payment-method-m2m`/`amount-by-group`/`tax-exigible`/`stock-inventory`/`phone-validation-mixin`）。
