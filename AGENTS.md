# AGENTS.md — 给 AI 代理的操作手册

本仓库是 **Odoo 自定义模块跨版本迁移工作台**，覆盖 **5→20** 的多个版本对。它把"升级知识"
沉淀为两类可复用产物，并配一套可执行的元技能（meta-skill）。

> **任何"如何制造迁移产物"的问题，先读 [`MigrationKnowledgeForge/SKILL.md`](./MigrationKnowledgeForge/SKILL.md)。**
> 本文件只给速览与红线，不重复元技能的细节。

---

## 1. 核心契约（必读）

每个版本对（如 `18.0 → 19.0`）**严格产出两份产物，且顺序不可颠倒**：

1. **Cookbook（迁移烹饪书）**——人读权威文档，先产出，是事实的唯一基准。
2. **Migration Skill（迁移技能，如 `Odoo18to19Migration/`）**——Cookbook 的"可执行压缩版"，
   后产出，必须与 Cookbook **事实对齐**（不得引入 Cookbook 之外的断言）。

两者冲突时，以 **Cookbook + 上游源（S1–S3）** 为准，并回填 Skill。

---

## 2. 目录速览

| 路径 | 作用 |
|---|---|
| `MigrationKnowledgeForge/` | **元技能**：构建任一版本对产物的方法论 + 脚本（pipeline A–F） |
| `Odoo19to20Migration/` | 已完成的 19→20 技能（SKILL + 6 份 references + 扫描器） |
| `Odoo18to19Migration/` | 已完成的 18→19 技能 + 配套 `Odoo_Migration_Cookbook_18_to_19.md` |
| `Odoo17to18Migration/` | 已完成的 17→18 技能 + 配套 `Odoo_Migration_Cookbook_17_to_18.md` |
| `Odoo16to17Migration/` | 已完成的 16→17 技能 + 配套 `Odoo_Migration_Cookbook_16_to_17.md`（**17.0 无 upgrade_code codemod，纯手工**） |
| `Odoo15to16Migration/` | 已完成的 15→16 技能 + 配套 `Odoo_Migration_Cookbook_15_to_16.md`（**16.0 无 upgrade_code codemod；DB 重命名由 OpenUpgrade 处理，支付/优惠券/模型改名手工**） |
| `Odoo14to15Migration/` | 已完成的 14→15 技能 + 配套 `Odoo_Migration_Cookbook_14_to_15.md`（**15.0 无 upgrade_code codemod；t-raw/ir.model*/Jinja/esm/资产/SavepointCase/Environment.manage/subtype 手工**） |
| `Odoo13to14Migration/` | 已完成的 13→14 技能 + 配套 `Odoo_Migration_Cookbook_13_to_14.md`（**14.0 无 upgrade_code codemod；ir.actions*/attrs/_name_search/name_get/force_company/Char-size/selection_add/TransientModel 手工**） |
| `Odoo12to13Migration/` | 已完成的 12→13 技能 + 配套 `Odoo_Migration_Cookbook_12_to_13.md`（**13.0 无 upgrade_code codemod；account.move/装饰器/customer_rank/binding/精度/tracking 手工**） |
| `Odoo11to12Migration/` | 已完成的 11→12 技能 + 配套 `Odoo_Migration_Cookbook_11_to_12.md`（**12.0 无 upgrade_code codemod；@api.one/fields.Date/model_create_multi/act_window.view 手工**） |
| `Odoo10to11Migration/` | 已完成的 10→11 技能 + 配套 `Odoo_Migration_Cookbook_10_to_11.md`（**11.0 无 upgrade_code codemod；Python3/Workflow 移除/报表 API 重写/模块改名手工**） |
| `Odoo9to10Migration/` | 已完成的 9→10 技能 + 配套 `Odoo_Migration_Cookbook_9_to_10.md`（**10.0 无 upgrade_code codemod；openerp→odoo/__openerp__→__manifest__ 手工**） |
| `Odoo8to9Migration/` | 已完成的 8→9 技能 + 配套 `Odoo_Migration_Cookbook_8_to_9.md`（**9.0 无 upgrade_code codemod；CE/EE 拆分/except_osv→UserError/osv_memory→transient 手工**） |
| `Odoo7to8Migration/` | 已完成的 7→8 技能 + 配套 `Odoo_Migration_Cookbook_7_to_8.md`（**8.0 无 upgrade_code codemod；New API/osv→models/osv.Model 手工**） |
| `Odoo6to7Migration/` | 已完成的 6→7 技能 + 配套 `Odoo_Migration_Cookbook_6_to_7.md`（**7.0 无 upgrade_code codemod；res.partner.address 移除/update_xml→data 手工**） |
| `Odoo5to6Migration/` | 已完成的 5→6 技能 + 配套 `Odoo_Migration_Cookbook_5_to_6.md`（**6.0 无 upgrade_code codemod；__terp__→__openerp__/init_xml 等合并手工**） |
| `Odoo_Migration_Cookbook_19_to_20.md` + `*.pdf` | 19→20 烹饪书（Markdown 统一卷 + 卷一修复版 + 卷二） |
| `Core_Models_Changelog.md` | **核心业务模型跨版本(5→20)变更追踪总表**：模型改名 / 字段增删 / 废弃 / 行为变化全局索引，含可信度与版本作用域红线 |
| `scripts/diff_core_models.py` | 跨版本模型/字段 diff 工具（本地 git 优先：`--repo`+`--ref-a/--ref-b`+`--scan-modules`/`--model`，自动定位模块目录；网络 `--pairs` 兜底），比对两版本 `_name`/`fields.X` 变化，生成可并入上表的 Markdown 清单 |
| `work/<version>/` | 各版本对的**中间产物归档**（研究来源、待核实追踪、一致性脚本；现含 `5to6` … `10to11` 与 `11to12` … `18to19`） |
| `FIX_NOTES.md` | 19→20 卷一 PDF 修复说明（裁切补全 + 信息抹除） |

---

## 3. 新增一个版本对（例如 17→18）

走元技能的 **pipeline F**：

1. 读 `MigrationKnowledgeForge/references/odoo-version-pairs.md` 的结构矩阵与预设。
2. `python3 MigrationKnowledgeForge/scripts/branch_diff.py --repo odoo/odoo --a 17.0 --b 18.0 --pairs "…" --kind defs|exports|classes|grep`
3. 用 `references/source-diff-mining.md` 的 **S1–S6 信源优先级**确认每条候选变更。
4. **先写 Cookbook**（pipeline C，单卷）。
5. **再写 Skill**（pipeline D，`MigrationKnowledgeForge/scripts/skill_scaffold.py`）。
6. 把研究来源 / 待核实追踪 / 一致性脚本归档到 `work/<version>/`。
7. 在根 `README.md` 的版本矩阵登记状态。

---

## 4. 红线（硬规则）

- **绝不臆造标识符**：查不到的 xml-id / 方法名一律标 `[verify]` 或 `[EE-verify]`，绝不静默"补全"。
- **严守版本作用域**：只收录"首次出现在 `[X.0, Y.0]`"的变更；更早版本（< X.0）或非 X→Y 的
  改动（如 `ir.access.csv`、`aggregator`、`tree→list`）**不得误带入**。
- **codemod 按 `--to` 生效**：`upgrade_code` 脚本只列真正会跑的（`--to Y.0` 下版本 ∈ [X.0, Y.0]）。
- **`references/` 份数/命名按需**：被生成的技能不强制六份、不固定文件名；代理应**动态枚举**
  `references/` 目录加载，不硬编码文件名。
- **溯源锚点必带**：每一行变更都引用 PR# / Changelog / codemod 脚本名 / 文件路径。
- **Cookbook 与 Skill 不得漂移**：修订后跑 `work/<version>/` 的一致性脚本（双向覆盖校验）。

---

## 5. 可用脚本（在 `MigrationKnowledgeForge/scripts/`）

| 脚本 | 用途 |
|---|---|
| `branch_diff.py` | 两个版本分支的 defs/classes/exports/grep 差异挖掘 |
| `skill_scaffold.py` | 生成新技能骨架（含 QA 脚本） |
| `pdf_extract.py` / `booklib.py` / `verify_pdf.py` | 裁切 PDF 修复 → 重排 → 溢出校验（0 越界 span） |
| `check_markdown.py` / `normalize_markdown.py` | Markdown 严格渲染兼容性 lint（须 0 issue） |

---

## 6. 质量门禁（交付前必须全绿）

- **Cookbook**：单卷；覆盖 X→Y 破坏面；版本作用域已核对；`[verify]`/`[EE-verify]` 已标；
  附溯源附录；渲染后 `verify_pdf.py` ⇒ 0 溢出 span。
- **Skill**：`references/` 与 Cookbook 同源；每行带溯源锚点；`upgrade_code` 清单真实生效；
  `check_markdown.py` ⇒ 0；扫描器 clean-addon ⇒ exit 0；一致性脚本 ⇒ 无漂移。

---

## 7. 不要做的事

- 不要跳过 Cookbook 直接写 Skill。
- 不要把 19→20 专属条目套用到低版本。
- 不要把 `work/<version>/` 的中间产物当作交付件发布（它是修订用的"记忆"）。
- 不要删除 `.workbuddy/` 目录（项目记忆，非临时缓存）。
