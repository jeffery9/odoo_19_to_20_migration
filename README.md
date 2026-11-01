# Odoo 版本迁移工作台（5 → 20）

本工作区用于 **Odoo 自定义模块跨版本迁移**，整合权威迁移烹饪书（Cookbook）与可复用的智能体技能（agent skill）。当前已覆盖 **5.0 → 6.0**、**6.0 → 7.0**、**7.0 → 8.0**、**8.0 → 9.0**、**9.0 → 10.0**、**10.0 → 11.0**、**11.0 → 12.0**、**12.0 → 13.0**、**13.0 → 14.0**、**14.0 → 15.0**、**15.0 → 16.0**、**16.0 → 17.0**、**17.0 → 18.0**、**18.0 → 19.0** 与 **19.0 → 20.0**（见下方版本覆盖矩阵，全矩阵已完成）。统一目标是：将低版本自定义插件（CE 与 EE）平滑升级到目标版本，且不留任何旧版本专属（*version-only*）API；其中 18.0 → 20.0 以 Odoo 自带 `upgrade_code` codemod 为主、以源码校验过的人工映射表为辅，而 5.0 → 17.0 全部为纯手工升级（无 `upgrade_code` 模块），需配合 OpenUpgrade 等社区工具。

## 版本覆盖矩阵

| 迁移路径 | 状态 | 烹饪书 / 资料 | 智能体技能 |
|---|---|---|---|
| **5.0 → 6.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_5_to_6.md`（单卷原创，14 章） | `Odoo5to6Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **6.0 → 7.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_6_to_7.md`（单卷原创，14 章） | `Odoo6to7Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **7.0 → 8.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_7_to_8.md`（单卷原创，15 章） | `Odoo7to8Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **8.0 → 9.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_8_to_9.md`（单卷原创，16 章） | `Odoo8to9Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **9.0 → 10.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_9_to_10.md`（单卷原创，17 章） | `Odoo9to10Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **10.0 → 11.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_10_to_11.md`（单卷原创，17 章） | `Odoo10to11Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **11.0 → 12.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_11_to_12.md`（单卷原创，13 章） | `Odoo11to12Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **12.0 → 13.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_12_to_13.md`（单卷原创，13 章） | `Odoo12to13Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **13.0 → 14.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_13_to_14.md`（单卷原创，12 章） | `Odoo13to14Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **14.0 → 15.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_14_to_15.md`（单卷原创，12 章） | `Odoo14to15Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **15.0 → 16.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_15_to_16.md`（单卷原创，11 章） | `Odoo15to16Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **16.0 → 17.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_16_to_17.md`（单卷原创，11 章） | `Odoo16to17Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **17.0 → 18.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_17_to_18.md`（单卷原创，11 章） | `Odoo17to18Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **18.0 → 19.0** | ✅ 已完成 | `Odoo_Migration_Cookbook_18_to_19.md`（单卷原创，10 章） | `Odoo18to19Migration/`（SKILL + 6 份参考表 + 扫描器） |
| **19.0 → 20.0** | ✅ 已完成 | 第一卷（修复版）+ 第二卷《Closing the Gaps》 + `Odoo_Migration_Cookbook_19_to_20.md`（Markdown 统一卷） | `Odoo19to20Migration/` |

> 每条迁移路径共用同一套方法论（扫描 → codemod → 人工映射 → 校验 → 报告）。技能将逐步参数化为**按目标版本加载对应映射表**，各版本差异表（ORM、安全、视图、API 等）复用本仓库已验证的格式与脚本。

## 目录结构

```
odoo_migration/
├── README.md                                   # 本文件（人读总览）
├── AGENTS.md                                   # 给 AI 代理的操作手册（速览 + 红线，指向元技能）
├── MigrationKnowledgeForge/                    # 元技能（meta-skill）：构建任一版本对烹饪书 + 迁移技能的方法论与脚本
├── FIX_NOTES.md                                # Volume I 修复说明（裁切补全 + 信息抹除）
├── Core_Models_Changelog.md                    # 核心业务模型跨版本(5→20)变更追踪总表（全局索引）
├── scripts/                                    # 跨版本工具
│   └── diff_core_models.py                       # 模型/字段 diff：比对两版本分支的 _name / _inherit / fields.X 变化
├── pdf/                                        # 成品 PDF（排版产物，不参与正文修订）
│   ├── Odoo_Migration_Cookbook_19_to_20_fixed.pdf    # 烹饪书 第一卷（修复版，50 页 A4）
│   └── Odoo_Migration_Cookbook_19_to_20_Vol2_Closing_the_Gaps.pdf  # 烹饪书 第二卷《Closing the Gaps》
├── Odoo_Migration_Cookbook_14_to_15.md            # 烹饪书 14→15（单卷原创，12 章）
├── Odoo_Migration_Cookbook_13_to_14.md            # 烹饪书 13→14（单卷原创，12 章）
├── Odoo_Migration_Cookbook_12_to_13.md            # 烹饪书 12→13（单卷原创，13 章）
├── Odoo_Migration_Cookbook_11_to_12.md            # 烹饪书 11→12（单卷原创，13 章）
├── Odoo_Migration_Cookbook_10_to_11.md            # 烹饪书 10→11（单卷原创，17 章）
├── Odoo_Migration_Cookbook_9_to_10.md             # 烹饪书 9→10（单卷原创，17 章）
├── Odoo_Migration_Cookbook_8_to_9.md              # 烹饪书 8→9（单卷原创，16 章）
├── Odoo_Migration_Cookbook_7_to_8.md              # 烹饪书 7→8（单卷原创，15 章）
├── Odoo_Migration_Cookbook_6_to_7.md              # 烹饪书 6→7（单卷原创，14 章）
├── Odoo_Migration_Cookbook_5_to_6.md              # 烹饪书 5→6（单卷原创，14 章）
├── Odoo_Migration_Cookbook_18_to_19.md            # 烹饪书 18→19（单卷原创，10 章）
├── Odoo_Migration_Cookbook_17_to_18.md            # 烹饪书 17→18（单卷原创，11 章）
├── Odoo_Migration_Cookbook_16_to_17.md            # 烹饪书 16→17（单卷原创，11 章）
├── Odoo_Migration_Cookbook_15_to_16.md            # 烹饪书 15→16（单卷原创，11 章）
├── uploads/                                    # 原始素材
│   ├── Odoo_Migration_Cookbook_19_to_20.pdf       # 原始第一卷（HeadlessChrome 打印，存在表格/代码行尾裁切）
│   └── Odoo_Migration_Cookbook_19_to_20_2col.md  # 双栏 Markdown 版（含 Mapping/Recovery 附录，补全依据来源）
├── work/                                       # 中间产物与可复现脚本（各版本按 <version>/ 子目录归档，供修订时复用）
│   ├── 18to19/                                   # 18→19 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（官方 Changelog PR + 社区来源 → 各自证实的变更）
│   │   ├── VERIFY_TRACKER.md                       # [verify]/[EE-verify] 待核实追踪表 + 修订 SOP
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验（修订时跑）
│   ├── 17to18/                                   # 17→18 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（18.0 源码核实记录）
│   │   ├── VERIFY_TRACKER.md                       # [verify] 待核实追踪表
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验
│   ├── 16to17/                                   # 16→17 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（17.0 源码核实记录）
│   │   ├── VERIFY_TRACKER.md                       # [verify]/[EE-verify] 待核实追踪表
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验
│   ├── 15to16/                                   # 15→16 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（16.0 源码核实记录）
│   │   ├── VERIFY_TRACKER.md                       # [verify]/[EE-verify] 待核实追踪表
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验
│   ├── 14to15/                                   # 14→15 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（15.0 源码核实记录）
│   │   ├── VERIFY_TRACKER.md                       # [verify]/[EE-verify] 待核实追踪表
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验
│   ├── 13to14/                                   # 13→14 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（14.0 源码核实记录）
│   │   ├── VERIFY_TRACKER.md                       # [verify] 待核实追踪表
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验
│   ├── 12to13/                                   # 12→13 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（13.0 源码核实记录）
│   │   ├── VERIFY_TRACKER.md                       # [verify] 待核实追踪表
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验
│   ├── 11to12/                                   # 11→12 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（12.0 源码核实记录）
│   │   ├── VERIFY_TRACKER.md                       # [verify] 待核实追踪表
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验
│   ├── 10to11/                                   # 10→11 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（11.0 源码核实记录）
│   │   ├── VERIFY_TRACKER.md                       # [verify] 待核实追踪表
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验
│   ├── 9to10/                                    # 9→10 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（10.0 源码核实记录）
│   │   ├── VERIFY_TRACKER.md                       # [verify] 待核实追踪表
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验
│   ├── 8to9/                                     # 8→9 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（9.0 源码核实记录）
│   │   ├── VERIFY_TRACKER.md                       # [verify] 待核实追踪表
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验
│   ├── 7to8/                                     # 7→8 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（8.0 源码核实记录）
│   │   ├── VERIFY_TRACKER.md                       # [verify] 待核实追踪表
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验
│   ├── 6to7/                                     # 6→7 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（7.0 源码核实记录）
│   │   ├── VERIFY_TRACKER.md                       # [verify] 待核实追踪表
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验
│   ├── 5to6/                                     # 5→6 中间产物
│   │   ├── RESEARCH_SOURCES.md                     # 研究来源查证地图（6.0 源码核实记录）
│   │   ├── VERIFY_TRACKER.md                       # [verify] 待核实追踪表
│   │   └── check_cookbook_consistency.py           # Cookbook↔Skill 一致性校验
│   ├── model.json / model_raw.json                # 提取+补全后的文档模型
│   ├── build_html.py / build_vol2.py              # 排版渲染脚本
│   ├── extract.py / patch_model.py                # 提取与补全脚本
│   ├── book.html / book.pdf / book2.*             # 渲染源与产物
│   ├── odoo20/                                   # 用于核实的 Odoo 20.0 源码片段
│   ├── demo_addons/ / uc/ / v2/                   # 验证用插件与对照图
│   └── *.png                                      # 修复前后页面对照截图
├── Odoo14to15Migration/                         # 智能体技能（agent skill），14→15
│   ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
│   ├── README.md                                  # 技能说明
│   ├── references/                                # 6 份参考表（views-qweb/orm-api/models-mapping/http-rpc-mail/security/upgrade-code）
│   └── scripts/                                   # 14→15 定制扫描器（t-raw/ir.model*/jinja/esm/assets/SavepointCase/Environment.manage/subtype）+ Markdown 工具
├── Odoo13to14Migration/                         # 智能体技能（agent skill），13→14
│   ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
│   ├── README.md                                  # 技能说明
│   ├── references/                                # 6 份参考表（orm-api/views-qweb/models-mapping/security/http-rpc-mail/upgrade-code）
│   └── scripts/                                   # 13→14 定制扫描器（ir.actions*/invisible-expr/_name_search/name_get/force_company/Char-size/selection-ondelete/stock-picking）+ Markdown 工具
├── Odoo12to13Migration/                         # 智能体技能（agent skill），12→13
│   ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
│   ├── README.md                                  # 技能说明
│   ├── references/                                # 6 份参考表（orm-api/accounting-models/views-qweb/models-mapping/security/upgrade-code）
│   └── scripts/                                   # 12→13 定制扫描器（api-decorators/dp.get_precision/track_visibility/oldname/account-invoice/partner-rank/src-model/act-window-multi/view-type/sudo-user/env-user-company/stock-quant-qty/tax-type）+ Markdown 工具
├── Odoo11to12Migration/                         # 智能体技能（agent skill），11→12
│   ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
│   ├── README.md                                  # 技能说明
│   ├── references/                                # 6 份参考表
│   └── scripts/                                   # 11→12 定制扫描器 + Markdown 工具
├── Odoo10to11Migration/                         # 智能体技能（agent skill），10→11
│   ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
│   ├── README.md                                  # 技能说明
│   ├── references/                                # 6 份参考表（orm-api/views-qweb/models-mapping/security/http-rpc-mail/upgrade-code）
│   └── scripts/                                   # 10→11 定制扫描器（py2-syntax/openerp-import/workflow/report-api/ir-cron-model/module-rename/module-merge/group-config）+ Markdown 工具
├── Odoo9to10Migration/                          # 智能体技能（agent skill），9→10
│   ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
│   ├── README.md                                  # 技能说明
│   ├── references/                                # 6 份参考表（orm-api/views-qweb/models-mapping/security/http-rpc-mail/upgrade-code）
│   └── scripts/                                   # 9→10 定制扫描器（openerp-import/manifest-rename/select-index/xml-selector/group-config/copy-decorator/group-move）+ Markdown 工具
├── Odoo8to9Migration/                           # 智能体技能（agent skill），8→9
│   ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
│   ├── README.md                                  # 技能说明
│   ├── references/                                # 6 份参考表
│   └── scripts/                                   # 8→9 定制扫描器（enterprise-split/except-osv/osv-memory-field/autovacuum）+ Markdown 工具
├── Odoo7to8Migration/                           # 智能体技能（agent skill），7→8
│   ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
│   ├── README.md                                  # 技能说明
│   ├── references/                                # 6 份参考表
│   └── scripts/                                   # 7→8 定制扫描器（api-decorators/self-pool/osv-model/except-osv/fields-attr/qweb-report）+ Markdown 工具
├── Odoo6to7Migration/                           # 智能体技能（agent skill），6→7
│   ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
│   ├── README.md                                  # 技能说明
│   ├── references/                                # 6 份参考表
│   └── scripts/                                   # 6→7 定制扫描器（osv-base/partner-address/manifest-keys/view-bootstrap）+ Markdown 工具
├── Odoo5to6Migration/                           # 智能体技能（agent skill），5→6
│   ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
│   ├── README.md                                  # 技能说明
│   ├── references/                                # 6 份参考表
│   └── scripts/                                   # 5→6 定制扫描器（terp-manifest/manifest-keys）+ Markdown 工具
├── Odoo16to17Migration/                         # 智能体技能（agent skill），16→17
│   ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
│   ├── README.md                                  # 技能说明
│   ├── references/                                # 6 份参考表（views/orm/http/security/modules/upgrade-code）
│   └── scripts/                                   # 16→17 定制扫描器 + Markdown 工具
├── Odoo15to16Migration/                         # 智能体技能（agent skill），15→16
│   ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
│   ├── README.md                                  # 技能说明
│   ├── references/                                # 6 份参考表（payment-loyalty/models/orm/views/security/upgrade-code）
│   └── scripts/                                   # 15→16 定制扫描器 + Markdown 工具
├── Odoo17to18Migration/                         # 智能体技能（agent skill），17→18
│   ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
│   ├── README.md                                  # 技能说明
│   ├── references/                                # 6 份参考表（views/orm/http/security/modules/upgrade-code）
│   └── scripts/                                   # 版本无关扫描器 + Markdown 工具
└── Odoo19to20Migration/                        # 智能体技能（agent skill），含独立 README.md
    ├── SKILL.md                                   # 技能 frontmatter + 工作流 + 硬规则
    ├── references/                                # 渐进式披露的源码校验映射表
    └── scripts/                                   # 扫描器与 Markdown 工具（纯标准库）
```

## 烹饪书（Cookbooks）

| 文件 | 覆盖版本 | 说明 |
|---|---|---|
| `Odoo_Migration_Cookbook_19_to_20.md` | 19.0 → 20.0 | 单卷原创烹饪书（Markdown 统一卷，12 章）：导言与版本作用域、框架与运行时（Python3.12 / `odoo.http` 包 / `odoo.osv` 移除 / `odoo.tools` 导出面）、安全文件 `security/ir.access.csv`（头号断裂）、ORM 与模型 API 重命名、`Domain` API 与 `read_group` 新签名、缓存/SQL/字段（`@api.ormcache` / `_table_sql` / `aggregator`）、视图/QWeb/Owl 3（kanban→card、图标、`t-set` 上提）、HTTP/邮件/二进制、模块/模型/字段映射、会计支付与 EE 专属、测试校验、`upgrade_code` codemod、迁移实战清单。基于 `odoo/upgrade_code` 脚本契约 + 19.0/20.0 分支源码核实（2026-10-11），与 `Odoo19to20Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_18_to_19.md` | 18.0 → 19.0 | 单卷原创烹饪书（10 章）：框架/运行时、ORM 与模型 API、安全与 res.groups、视图/QWeb/Owl 3、HTTP/邮件/二进制、模块/模型/字段映射、缓存/SQL、测试校验、upgrade_code codemod、迁移实战清单。基于官方 ORM Changelog + 多社区源（Cybrosys、SDLC、ERP24、Octura、LineScripts、DeployMonkey、mindscript）交叉核实，与 `Odoo18to19Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_17_to_18.md` | 17.0 → 18.0 | 单卷原创烹饪书（11 章）：导言与版本作用域、`tree`→`list` 头号断裂、ORM/模型 API 移除（name_get / _name_search / check_access 合并 / user_has_groups / check_recursion）、字段属性 aggregator、HTTP 路由 jsonrpc、安全与 res.groups（17→18 不变）、视图/QWeb 前端、模块/模型/字段映射、缓存/SQL、测试校验、upgrade_code codemod、迁移实战清单。基于官方 18.0 ORM Changelog + 18.0 源码核实（ir_ui_view.py / models.py / upgrade_code/）+ OCA/Cybrosys/ODIWARE/DeployMonkey 交叉核实，与 `Odoo17to18Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_16_to_17.md` | 16.0 → 17.0 | 单卷原创烹饪书（11 章）：导言与版本作用域、视图语法革命（`attrs`/`states` 硬拒→内联表达式、`column_invisible`、`res.config.settings` 简化、`active_*` context）、Python 底座抬升（Python 3.10、钩子 `env`、`get_resource_path`→`file_path`、`message_post` body）、**17.0 无 `upgrade_code` codemod**（纯手工）、SCSS 在 17.0 仍编译（纠偏误传）。基于 OCA《Migration to version 17.0》框架清单（PR #104741/#106425/#122085/#135607/b4a7996/daf05d48）+ 17.0 源码核实（ir_ui_view.py 的 attrs/states 硬拒、tools/misc.py 的 get_resource_path 移除、requirements.txt 的 libsass/Werkzeug、upgrade_code/ 缺失）+ 多社区源交叉核实，与 `Odoo16to17Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_15_to_16.md` | 15.0 → 16.0 | 单卷原创烹饪书（11 章）：导言与版本作用域（排除 attrs/states/tree/name_get/get_resource_path — 这些在 16.0 仍合法）、支付系统重构（头号断裂 `payment.acquirer`→`payment.provider` + `acquirer_id`/`provider_reference`/`_handle_feedback_data` 改名）、优惠券→忠诚度（`coupon.*`→`loyalty.*`）、翻译表移除（`ir_translation`→JSONB）、批量模型/模块改名（`stock.lot`/`account_analytic.plan`/`mail.channel.member`/`account.report`/`account_type`）、`track_visibility`→`tracking` 与 `api.multi` 移除、视图在 15→16 几乎不变、安全文件/res.groups 不变、**16.0 无 `upgrade_code` codemod**（DB 重命名由 OpenUpgrade 处理）。基于 OCU 15→16 结构差异统计 + oejia 支付改名明细 + DeployMonkey + 16.0 源码核实（release.py、ir_ui_view.py L82–96/L237、models.py 的 name_get 等仍在、modules/module.py 的 get_resource_path 仍在、api.py 无 api.multi、upgrade_code/ 缺失），与 `Odoo15to16Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_14_to_15.md` | 14.0 → 15.0 | 单卷原创烹饪书（12 章）：导言与版本作用域、`t-raw`→`t-out`/`t-esc`（头号断裂，配 `markupsafe.Markup`）、`ir.model*` 对象访问移除（#69120）、邮件模板 Jinja→QWeb 正文 + `inline_template`（#77074）、前端 ES 模块 `.esm.js` + 资产声明进 `__manifest__.py` `assets` 键（`qweb` 键移除）、测试 `SavepointCase`→`TransactionCase`（#62031）与 `Environment.manage()` 移除、安全与 `res.groups` 不变、`subtype`→`subtype_xmlid`（[verify]）、模块/模型/字段映射、测试校验、14→15 无 `upgrade_code` codemod、迁移实战清单。基于 OCA 15.0 官方指南 + odoo/odoo #69120/#77074/#62031/01875541b1a8 + 多社区源交叉核实，与 `Odoo14to15Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_13_to_14.md` | 13.0 → 14.0 | 单卷原创烹饪书（12 章）：导言与版本作用域、`ir.actions.*` 直接访问移除（#53335）、`invisible`/`readonly` 动态表达式→`attrs` 域、`_name_search` 返回 ids（1f48130）、`_compute_display_name`→`name_get`、`force_company`→`with_company`、`Char` `size` 属性移除、`selection_add` 须 `ondelete`、`TransientModel` 显式 ACL、`stock.picking` 字段改名（[verify]）、安全与 `res.groups` 不变、模块/模型/字段映射、测试校验、13→14 无 `upgrade_code` codemod、迁移实战清单。基于 OCA 14.0 官方指南 + odoo/odoo #53335/1f48130/f0481392 + 多社区源交叉核实，与 `Odoo13to14Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_12_to_13.md` | 12.0 → 13.0 | 单卷原创烹饪书（13 章）：导言与版本作用域、会计重写 `account.invoice`→`account.move`（头号断裂）、ORM 装饰器清理（@api.multi/returns/cr/model_cr 移除）、`customer`/`supplier`→`customer_rank`/`supplier_rank`、`src_model`/`multi`→`binding_model_id`/`binding_view_types`、`dp.get_precision`→`digits`、`track_visibility`→`tracking`、`oldname` 移除、`stock.quant` `qty`→`quantity`、`product.product` name related、`account.tax` `type`→`type_tax_use`、`sudo(user)`→`with_user`、`.env.user.company_id`→`.env.company`、安全与 `res.groups` 不变、视图/QWeb、HTTP/邮件/二进制、模块/模型/字段映射、测试校验、12→13 无 `upgrade_code` codemod、迁移实战清单。基于 OCA 13.0 官方指南 + 多社区源交叉核实，与 `Odoo12to13Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_11_to_12.md` | 11.0 → 12.0 | 单卷原创烹饪书（13 章）：导言与版本作用域、`@api.one` 装饰器移除（头号断裂）、`fields.Date` 运行时类型革命、`@api.model_create_multi` 与 `_parent_store`、`ir.actions.act_window.view` 移除、字段与数据模型、视图/QWeb/前端、HTTP/邮件/二进制、安全与 `res.groups`（11→12 不变）、模块/模型/字段映射、测试与校验、11→12 无 `upgrade_code` codemod、迁移实战清单。基于 OCA 12.0 官方指南 + 多社区源交叉核实，与 `Odoo11to12Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_10_to_11.md` | 10.0 → 11.0 | 单卷原创烹饪书（17 章）：导言与版本作用域、Python 3 强制（头号断裂，`print` 语句 / `iteritems` / `itervalues` / `has_key` / `xrange` / `except` 元组 / `basestring` 等全部非法）、`openerp` 兼容别名清理（包改名 `openerp`→`odoo` 已在 9→10 完成，本卷清最后别名）、Workflow 完全移除（`wkf` 模型与 `workflow.*` API）、QWeb 报表 API 重写（`render_html`→`get_report_values`、`get_action`→`report_action`）、`ir.cron` `model`→`model_id`、`sale`→`sale_management` / `account_accountant`→`account_invoicing` 改名、`account_tax_cash_basis`→`account` / `report`→`web` 合并、`base.group_configuration`→`base.group_system`。基于 OCA 11.0 官方指南 + 多社区源交叉核实，与 `Odoo10to11Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_9_to_10.md` | 9.0 → 10.0 | 单卷原创烹饪书（17 章）：导言与版本作用域、`openerp`→`odoo` 包改名 + `__openerp__.py`→`__manifest__.py`（头号断裂，9→10 完成包级更名与清单文件名标准化）、`select` 索引声明、`xml` 选择器、`group` 配置模块化、`copy` 装饰器、group 字段迁移等。基于 OCA 10.0 官方指南 + 多社区源交叉核实，与 `Odoo9to10Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_8_to_9.md` | 8.0 → 9.0 | 单卷原创烹饪书（16 章）：导言与版本作用域、Community/Enterprise 拆分（头号断裂，`addons` 路径与 `auto_install` 模块分发）、`osv.except_osv`→`UserError`、`osv_memory`→`transient`（TransientModel 字段 / ACL）、`_autovacuum` 线程移除。基于 OCA 9.0 官方指南 + 多社区源交叉核实，与 `Odoo8to9Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_7_to_8.md` | 7.0 → 8.0 | 单卷原创烹饪书（15 章）：导言与版本作用域、完整 New API（头号断裂，`osv`→`models` 导入、`self.env`、`@api.multi` / `@api.model` / `@api.one` / `@api.depends` / `@api.constrains`、recordset 运算、`osv.except_osv`→`UserError`、字段改为类属性）、`self.pool`→`self.env`、`osv.Model`→`models.Model` 基类、`QWeb` 报表引入。基于 OCA 8.0 官方指南 + 多社区源交叉核实，与 `Odoo7to8Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_6_to_7.md` | 6.0 → 7.0 | 单卷原创烹饪书（14 章）：导言与版本作用域、`res.partner.address` 模型移除（头号断裂，地址合并进 `res.partner`）、`__manifest__.py` `update_xml`→`data` 收尾、基类 `osv.osv`→`osv.Model` 改名起始、视图 Bootstrap 化。基于 OCA 7.0 官方指南 + 多社区源交叉核实，与 `Odoo6to7Migration/` 技能事实对齐。 |
| `Odoo_Migration_Cookbook_5_to_6.md` | 5.0 → 6.0 | 单卷原创烹饪书（14 章）：导言与版本作用域、`__terp__.py`→`__openerp__.py` 清单文件改名（头号断裂）、`init_xml` / `update_xml` / `demo_xml`→`data` / `demo` / `test` 清单键收尾、manifest 键规范化。基于 OCA 6.0 官方指南 + 多社区源交叉核实，与 `Odoo5to6Migration/` 技能事实对齐。 |
| `pdf/Odoo_Migration_Cookbook_19_to_20_fixed.pdf` | 19.0 → 20.0 | 第一卷修复版。原版由 HeadlessChrome 打印，表格与代码块置于横向滚动容器内，打印时右边界在 `x ≈ 547.7pt` 处被硬裁切，导致 10 个页面的表格右列内容、4 处代码块行尾被截断。修复版用 PyMuPDF 反向提取文档模型并对裁切单元格/代码行补全，再以 WeasyPrint 重新排版（页宽固定布局 + 单元格内自动换行），全篇 **0 个越界文本 span**（原版 45 处）。 |
| `pdf/Odoo_Migration_Cookbook_19_to_20_Vol2_Closing_the_Gaps.pdf` | 19.0 → 20.0 | 第二卷《Closing the Gaps》，补齐第一卷未覆盖的运行时/导入、缓存与 SQL、模型 API、字段与测试等差异。 |

详细的裁切原因、补全清单（33 处表格 + 3 处代码行，标注【源码】/【md】/【重构】依据）以及出版商信息抹除记录，见 [`FIX_NOTES.md`](./FIX_NOTES.md)。

## 核心业务模型变更追踪（跨版本索引）

[`Core_Models_Changelog.md`](./Core_Models_Changelog.md) 是 **Odoo 标准核心业务模型**（会计/销售/采购/库存/伙伴/产品/HR/项目/邮件/支付等）在 **5.0 → 20.0** 全部 15 条版本对上的演变**全局索引**：模型改名、字段增删/改名、模型废弃、关键行为变化，每行标注可信度（`CONFIRMED` / `[verify]` / `[EE-verify]`）、自动化方式（`codemod:xxx` / `OpenUpgrade` / 手工）与来源（对应版本对烹饪书或 `OdooXXtoYYMigration/references/`）。它是各版本对 references 的"跨版本汇总"，二者同源、互为索引；并附**版本作用域红线**（防误归，如 `account.invoice`→`account.move` 仅属 12→13）。

配套脚本 [`scripts/diff_core_models.py`](./scripts/diff_core_models.py) 对标 `MigrationKnowledgeForge/scripts/branch_diff.py`。**首选本地 git 模式**：`--repo` 指向本机 `odoo` / `odoo-enterprise` checkout，`--ref-a/--ref-b` 指定两版本，用 `git show <ref>:<path>` 读真实源码，AST 提取 `_name` / `_inherit` / `fields.X`；支持 `--scan-modules`（模块内模型集 diff）与 `--model`（单模型字段级 diff，自动定位并聚合所有定义/继承文件），输出可直接并入上述总表的 Markdown 清单（含离线 `--self-test`）。无本地仓库时可退回网络 `--pairs` 模式。

## 智能体技能（OdooXXtoYYMigration）

每个版本对一个独立技能目录，均兼容 agent-skills 格式（`SKILL.md`），将对应烹饪书/官方升级资料的要点压缩为源码校验过的映射表，并配合 Odoo 自带 `odoo-bin upgrade_code` codemod 使用。

| 技能目录 | 覆盖 | 状态 |
|---|---|---|
| `Odoo19to20Migration/` | 19.0 → 20.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、扫描器） |
| `Odoo18to19Migration/` | 18.0 → 19.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、扫描器；配套 `Odoo_Migration_Cookbook_18_to_19.md`） |
| `Odoo17to18Migration/` | 17.0 → 18.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、扫描器；配套 `Odoo_Migration_Cookbook_17_to_18.md`） |
| `Odoo16to17Migration/` | 16.0 → 17.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、定制扫描器；配套 `Odoo_Migration_Cookbook_16_to_17.md`） |
| `Odoo15to16Migration/` | 15.0 → 16.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、定制扫描器；配套 `Odoo_Migration_Cookbook_15_to_16.md`） |
| `Odoo14to15Migration/` | 14.0 → 15.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、定制扫描器；配套 `Odoo_Migration_Cookbook_14_to_15.md`） |
| `Odoo13to14Migration/` | 13.0 → 14.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、定制扫描器；配套 `Odoo_Migration_Cookbook_13_to_14.md`） |
| `Odoo12to13Migration/` | 12.0 → 13.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、定制扫描器；配套 `Odoo_Migration_Cookbook_12_to_13.md`） |
| `Odoo11to12Migration/` | 11.0 → 12.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、定制扫描器；配套 `Odoo_Migration_Cookbook_11_to_12.md`） |
| `Odoo10to11Migration/` | 10.0 → 11.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、定制扫描器；配套 `Odoo_Migration_Cookbook_10_to_11.md`） |
| `Odoo9to10Migration/` | 9.0 → 10.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、定制扫描器；配套 `Odoo_Migration_Cookbook_9_to_10.md`） |
| `Odoo8to9Migration/` | 8.0 → 9.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、定制扫描器；配套 `Odoo_Migration_Cookbook_8_to_9.md`） |
| `Odoo7to8Migration/` | 7.0 → 8.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、定制扫描器；配套 `Odoo_Migration_Cookbook_7_to_8.md`） |
| `Odoo6to7Migration/` | 6.0 → 7.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、定制扫描器；配套 `Odoo_Migration_Cookbook_6_to_7.md`） |
| `Odoo5to6Migration/` | 5.0 → 6.0 | ✅ 已完成（含 `README.md`、`SKILL.md`、6 份参考表、定制扫描器；配套 `Odoo_Migration_Cookbook_5_to_6.md`） |

> 首个落地实现是 `Odoo19to20Migration/`，其结构作为后续版本的参考范式。各技能共用同一套版本无关扫描器（`scripts/scan_addon.py` 等），各自维护独立的 `references/` 映射表。

> **构建方法论（元技能）**见 [`MigrationKnowledgeForge/`](./MigrationKnowledgeForge/SKILL.md)：从 19→20 实践提炼、并融合各版本对经验的"如何造版本迁移产物"可复用 meta-skill。核心契约：**每个版本对产出两份产物（先 Cookbook 后 Skill）**；内含来源优先级 S1–S6、版本作用域纪律、`work/<version>/` 中间产物归档、`branch_diff.py` 源码挖差、`skill_scaffold.py` 技能骨架等流水线。新增任一版本对（如 18→19 / 17→18 / … / 5→6，含本次新增的 10→11、9→10、8→9、7→8、6→7、5→6）时按此执行即可。

**18→19 工作流**：扫描（triage）→ 跑 codemod（`upgrade_code --from 18.0`，从 19.0 安装运行）→ 应用 `Odoo18to19Migration/references/` 人工映射 → 校验（`-u` + 测试 + 清 DeprecationWarning）→ 出报告。

**17→18 工作流**：扫描（triage）→ 跑 codemod（`upgrade_code --from 17.0`，从 18.0 安装运行，**仅 `tree`→`list` 一项**）→ 应用 `Odoo17to18Migration/references/` 人工映射（name_get / check_access / user_has_groups / aggregator / jsonrpc 等均需手动）→ 校验（`-u` + 测试 + 清 DeprecationWarning）→ 出报告。

**16→17 工作流**：扫描（triage）→ **无 codemod**（17.0 无 `upgrade_code` 模块，全部手工）→ 应用 `Odoo16to17Migration/references/` 人工映射（`attrs`/`states`→内联表达式、`column_invisible`、`res.config.settings` 简化、钩子 `env`、`get_resource_path`→`file_path`、`active_*` context、`message_post` body）→ 数据迁移写模块 `migrations/17.0/` → 校验（`-u` + 测试 + 清 DeprecationWarning）→ 出报告。

**15→16 工作流**：① 数据库迁移（OpenUpgrade 社区版 / 官方升级服务，自动完成模型/字段/模块改名、`ir_translation`→JSONB、模块合并、约束应用）→ ② 扫描（triage，`Odoo15to16Migration/scripts/scan_addon.py`，**无 codemod**，全部手工）→ ③ 应用 `Odoo15to16Migration/references/` 人工映射（支付 `payment.acquirer`→`payment.provider` + 字段/方法改名、优惠券 `coupon`→`loyalty`、`stock.lot`/`account_analytic.plan`/`mail.channel.member`/`account.report` 等模型改名、`ir_translation` 直读写改写、`track_visibility`→`tracking`、`api.multi` 删除）→ ④ 数据迁移写模块 `migrations/16.0/` → ⑤ 校验（重扫期望 0、`-u` + 测试、清 `ImportError`/`Model not available`）→ 出报告。

**14→15 工作流**：① 数据库迁移（OpenUpgrade 社区版 / 官方升级服务，自动完成 DB 级变更）→ ② 扫描（triage，`Odoo14to15Migration/scripts/scan_addon.py`，**无 codemod**，全部手工）→ ③ 应用 `Odoo14to15Migration/references/` 人工映射（`t-raw`→`t-out`/`t-esc` + `markupsafe.Markup`、`ir.model*` 访问 sudo 化、`mail.template` Jinja→QWeb 正文 + `inline_template`、`*.esm.js` 改名、资产声明移入 `__manifest__.py` `assets` 键、`SavepointCase`→`TransactionCase`、`Environment.manage()` 移除、`subtype`→`subtype_xmlid` [verify]）→ ④ 数据迁移写模块 `migrations/15.0/`（subtype_xmlid xmlid、资产移动等）→ ⑤ 校验（重扫期望 0、`-u` + 测试、清 `ImportError`/`AttributeError`）→ 出报告。

**13→14 工作流**：① 数据库迁移（OpenUpgrade 社区版 / 官方升级服务）→ ② 扫描（triage，`Odoo13to14Migration/scripts/scan_addon.py`，**无 codemod**，全部手工）→ ③ 应用 `Odoo13to14Migration/references/` 人工映射（`ir.actions.*` 访问改用 `_for_xml_id`/`sudo`、`invisible`/`readonly` 动态表达式→`attrs`、`_name_search` 返回 ids、`_compute_display_name`→`name_get`、`force_company`→`with_company`、`Char` `size` 移除、`selection_add` 加 `ondelete`、`TransientModel` 补 ACL、`stock.picking` 字段改名 [verify]）→ ④ 数据迁移写模块 `migrations/14.0/`（selection 选项迁移等）→ ⑤ 校验（重扫期望 0、`-u` + 测试）→ 出报告。

**12→13 工作流**：① 数据库迁移（OpenUpgrade 社区版 / 官方升级服务，会计 `account.invoice`→`account.move` 等 DB 级重构）→ ② 扫描（triage，`Odoo12to13Migration/scripts/scan_addon.py`，**无 codemod**，全部手工）→ ③ 应用 `Odoo12to13Migration/references/` 人工映射（会计模型合并、`@api.multi` 等装饰器清理、`customer`/`supplier`→`customer_rank`/`supplier_rank`、`src_model`/`multi`→`binding_model_id`/`binding_view_types`、`dp.get_precision`→`digits`、`track_visibility`→`tracking`、`oldname` 移除、`stock.quant` `qty`→`quantity`、`sudo(user)`→`with_user`、`.env.user.company_id`→`.env.company`）→ ④ 数据迁移写模块 `migrations/13.0/`（oldname 改名、Binary 默认附件等）→ ⑤ 校验（重扫期望 0、`-u` + 测试）→ 出报告。

**11→12 工作流**：① 数据库迁移（OpenUpgrade 社区版 / 官方升级服务）→ ② 扫描（triage，`Odoo11to12Migration/scripts/scan_addon.py`，**无 codemod**，全部手工）→ ③ 应用 `Odoo11to12Migration/references/` 人工映射（`@api.one` 移除、`fields.Date` 运行时类型改写、`@api.model_create_multi` 与 `_parent_store`、`ir.actions.act_window.view` 移除）→ ④ 数据迁移写模块 `migrations/12.0/` → ⑤ 校验（重扫期望 0、`-u` + 测试）→ 出报告。

**10→11 工作流**：① 数据库迁移（OpenUpgrade 社区版 / 官方升级服务）→ ② 扫描（triage，`Odoo10to11Migration/scripts/scan_addon.py`，**无 codemod**，全部手工）→ ③ 应用 `Odoo10to11Migration/references/` 人工映射（Python 3 语法修正、`openerp` 别名清理、Workflow 移除、QWeb 报表 API 重写、`ir.cron` `model`→`model_id`、模块改名 `sale`→`sale_management` / `account_accountant`→`account_invoicing`、合并 `account_tax_cash_basis`→`account` / `report`→`web`、`base.group_configuration`→`base.group_system`）→ ④ 数据迁移写模块 `migrations/11.0/` → ⑤ 校验（重扫期望 0、`-u` + 测试、清 `SyntaxError` / `ImportError`）→ 出报告。

**9→10 工作流**：① 数据库迁移（OpenUpgrade 社区版 / 官方升级服务）→ ② 扫描（triage，`Odoo9to10Migration/scripts/scan_addon.py`，**无 codemod**，全部手工）→ ③ 应用 `Odoo9to10Migration/references/` 人工映射（`openerp`→`odoo` 包改名、`__openerp__.py`→`__manifest__.py`、`select` 索引、`xml` 选择器、`group` 配置模块化、`copy` 装饰器、group 字段迁移）→ ④ 数据迁移写模块 `migrations/10.0/` → ⑤ 校验（重扫期望 0、`-u` + 测试）→ 出报告。

**8→9 工作流**：① 数据库迁移（OpenUpgrade 社区版 / 官方升级服务，含 CE/EE 拆分）→ ② 扫描（triage，`Odoo8to9Migration/scripts/scan_addon.py`，**无 codemod**，全部手工）→ ③ 应用 `Odoo8to9Migration/references/` 人工映射（CE/EE 拆分路径与 `auto_install`、`osv.except_osv`→`UserError`、`osv_memory`→`transient`、`_autovacuum` 移除）→ ④ 数据迁移写模块 `migrations/9.0/` → ⑤ 校验（重扫期望 0、`-u` + 测试）→ 出报告。

**7→8 工作流**：① 数据库迁移（OpenUpgrade 社区版 / 官方升级服务）→ ② 扫描（triage，`Odoo7to8Migration/scripts/scan_addon.py`，**无 codemod**，全部手工）→ ③ 应用 `Odoo7to8Migration/references/` 人工映射（`osv`→`models` 导入、New API 装饰器、recordset 运算、`osv.Model`→`models.Model`、`self.pool`→`self.env`、`QWeb` 报表）→ ④ 数据迁移写模块 `migrations/8.0/` → ⑤ 校验（重扫期望 0、`-u` + 测试）→ 出报告。

**6→7 工作流**：① 数据库迁移（OpenUpgrade 社区版 / 官方升级服务）→ ② 扫描（triage，`Odoo6to7Migration/scripts/scan_addon.py`，**无 codemod**，全部手工）→ ③ 应用 `Odoo6to7Migration/references/` 人工映射（`res.partner.address`→`res.partner` 合并、`update_xml`→`data`、基类 `osv.osv`→`osv.Model`、视图 Bootstrap 化）→ ④ 数据迁移写模块 `migrations/7.0/` → ⑤ 校验（重扫期望 0、`-u` + 测试）→ 出报告。

**5→6 工作流**：① 数据库迁移（OpenUpgrade 社区版 / 官方升级服务）→ ② 扫描（triage，`Odoo5to6Migration/scripts/scan_addon.py`，**无 codemod**，全部手工）→ ③ 应用 `Odoo5to6Migration/references/` 人工映射（`__terp__.py`→`__openerp__.py`、`init_xml` / `update_xml` / `demo_xml`→`data` / `demo` / `test`、manifest 键规范化）→ ④ 数据迁移写模块 `migrations/6.0/` → ⑤ 校验（重扫期望 0、`-u` + 测试）→ 出报告。

**19→20 工作流**：扫描（triage）→ 跑 codemod（`upgrade_code --from 19.0`）→ 应用 `Odoo19to20Migration/references/` 人工映射 → 校验（`-u` + 测试）→ 出报告。

**六大参考表**（`Odoo19to20Migration/references/`）：

- `security-and-orm.md` — `ir.access.csv`、ORM 重命名、domains / `read_group`
- `binary-http-mail.md` — binary/Excel/PDF/时间、HTTP 路由、邮件、SQL 报告
- `views-qweb-owl.md` — 视图 xpath、ribbon/icon、看板卡片、QWeb 与 Owl 3
- `modules-mapping.md` — 各业务模块的模型/字段/xml-id 映射 + 症状索引
- `api-deltas-vol2.md` — 运行时/导入、缓存与 SQL、模型 API、字段、测试
- `upgrade-code.md` — `upgrade_code` 用法 + 脚本契约

**快速试用**：

```bash
# 1. 扫描插件树（exit 1 = 有发现）
python3 Odoo19to20Migration/scripts/scan_addon.py /path/to/addons --addon my_module

# 2. 在干净的 git 分支上先 dry-run 再正式跑 codemod
odoo-bin upgrade_code --from 19.0 --addons-path /path/to/addons --dry-run
odoo-bin upgrade_code --from 19.0 --addons-path /path/to/addons

# 3. 在 20.0 沙箱中校验
odoo-bin -u my_module --test-tags /my_module
```

安装与完整用法见 [`Odoo19to20Migration/README.md`](./Odoo19to20Migration/README.md)。

## 数据来源与校验

- 映射表条目均对照 `github.com/odoo/odoo` 的**对应版本分支**（如 19→20 对照 `19.0` / `20.0`，18→19 对照 `18.0` / `19.0`，5→6 对照 `5.0` / `6.0`，依此类推）核实（19→20 基准日 2026-10-11；5→11 各版本对的核实日见各自 `work/<version>/RESEARCH_SOURCES.md`）。
- 标注 **[EE-verify]** 的条目仅适用于 Enterprise；部署前必须对照**目标版本的 Enterprise 源码树**复核，不得当作已验证内容呈现。
- 不要臆造 XML-ID 或方法名：均须在上游目标版本树或带源码出处的映射表中查证；无法核实的 EE id 保持标记，绝不静默"补全"。

## 注意事项

- 各版本迁移的 codemod 依赖 Odoo 自带的 `odoo-bin upgrade_code`；请注意该能力自 Odoo 提供 `upgrade_code` 模块的版本起可用（18.0+），因此 **5.0 → 17.0 全部为纯手工升级（无 codemod）**，需配合手动脚本或第三方升级工具（OpenUpgrade）作为补充；**18.0 → 20.0** 才可使用 codemod。
- 修复版（第一卷）已按需求抹除原出版商（Probuse Consulting Service Pvt. Ltd.）的全部联系与版权信息，仅保留作者姓名及改写后的个人简介。
- 第一卷修复版中少量【重构】标注的单元格/代码行为语义补全，建议人工复核；涉及 Enterprise 的内容需结合 EE 源码确认。
- `work/` 与 `uploads/` 为过程产物与原始素材，非交付件；发布或归档时按需裁剪。
