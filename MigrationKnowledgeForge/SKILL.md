---
name: migration_knowledge_forge
description: Meta-skill that manufactures migration knowledge artifacts for ANY Odoo version pair (17→18, 18→19, 19→20, …; other products by parameterization). Enforces a two-artifact contract per version pair — a Cookbook (authored first, the source of truth) and a Migration Skill (forged second, fact-aligned to the Cookbook). Use when asked to (a) repair a clipped/broken source PDF book and rebuild it as a clean cookbook, (b) author a new migration cookbook volume from two version branches, (c) mine verified API deltas between two versions (def/export/keyword diffs with provenance), or (d) scaffold a new migration agent skill (SKILL.md + references + scanner + markdown QA). Encapsulates the pipelines, design system, version-pair profiles, version-scope discipline and QA gates used to produce the Odoo 19→20 cookbook Volume I (fixed edition), Volume II and the odoo_19_to_20_migration skill.
version: 1.0.0
author: Independent (forge of the Odoo Migration Cookbook I/II + odoo_19_to_20_migration skill)
category: meta
odoo_versions: ["any"]
tags: [meta, cookbook, pdf-repair, weasyprint, skill-authoring, source-diff, provenance, markdown-qa]
---

# Migration Knowledge Forge (meta-skill)

## Goal

Turn *raw migration evidence* (a clipped PDF book, two source branches, a set of
deprecation greps) into *shippable migration artifacts*: a typeset cookbook PDF
and/or an agent skill with verified reference tables and a CI scanner.

## Product contract (two artifacts, strict order)

A version pair (Odoo X.0 → Y.0) always ships **exactly two artifacts, in this order**:

1. **Cookbook** — the human-readable authoritative migration book: every real X→Y
   breaking change, written "background + Before/After + source + verify status".
   Produced **first**; it is the single source of truth for facts.
2. **Migration Skill** (`OdooXXtoYYMigration/`) — the executable agent skill: Cookbook
   facts compressed into provenance-tagged `references/` tables + an `upgrade_code`
   codemod hook. Produced **second**; must stay fact-aligned to the Cookbook (no new claims).

Order is non-negotiable: the Skill is the Cookbook's *executable compression*, not an
independent source. On any conflict, the Cookbook + upstream sources (S1–S3 in
`references/source-diff-mining.md`) win and the Skill is patched back.

## Pipelines (pick by input)

| Input | Pipeline | Entry points |
|---|---|---|
| PDF whose tables/code are clipped at a container edge | A. Repair & rebuild | `scripts/pdf_extract.py` → completion pass → `scripts/booklib.py` → `scripts/verify_pdf.py`; procedure in `references/cookbook-pipeline.md` |
| Two version branches (git refs) of a product | B. Mine verified deltas | `scripts/branch_diff.py` + rules in `references/source-diff-mining.md` |
| Verified delta notes that must become a book | C. Author a cookbook volume | `scripts/booklib.py` (design system in `references/design-system.md`) |
| Verified delta notes that must become an agent skill | D. Forge a skill | `scripts/skill_scaffold.py` + conventions in `references/skill-authoring.md` |
| Any markdown/PDF artifact produced here | E. QA gate | `scripts/check_markdown.py`, `scripts/normalize_markdown.py`, `scripts/verify_pdf.py` |
| A new Odoo version pair (5→6 … 19→20) | F. Instantiate pair | `references/odoo-version-pairs.md` (matrix, presets, codemod-target rule) + `scripts/branch_diff.py` |
| Cross-version core-model tracking (≥2 pairs exist) | G. Cross-version index | `references/cross-version-models.md` + `references/version-scope-redlines.md` + `scripts/diff_core_models.py` |

## Instantiating a version pair (pipeline F)

1. Read the structural matrix in `references/odoo-version-pairs.md` (models layout,
   orm/osv/http package era, upgrade_code availability, view type, Python floor).
2. Run the pair preset of `scripts/branch_diff.py` (old-path:new-path pairs where modules moved).
3. Codemods: always run `upgrade_code` from the **target** branch; no codemods for targets ≤17.
4. Continue with pipelines **B → C (cookbook first) → D (skill second)** using
   `--versions "<old>,<new>"` everywhere. If a cookbook already exists, B → D suffices.
   The Skill must derive from the Cookbook — never authored independently.

## Completion / provenance hierarchy (mandatory)

When source content is missing (clipped cells, renamed APIs), complete it in this order and
record the tier for every completed value:

1. **Uploaded/derived doc** — the same value visible elsewhere in the corpus (cross-page, appendix).
2. **Public source tree** — verify against the target branch file (fetch raw, grep, quote the file).
3. **Reconstruction** — semantics/parallel phrasing; MUST be flagged in the book changelog and,
   for Enterprise-only items, tagged **[EE-verify]** (never presented as verified).

Never invent identifiers: an xml-id/method name that cannot be located in the target tree stays
unwritten or flagged.

## Hard rules

- **Version-scope red lines (mandatory, first check):** before listing any breaking change
  in an X→Y artifact, confirm it *first appears at ≥ X.0 and ≤ Y.0*. Consult
  `references/version-scope-redlines.md` — the forge's canonical ownership table. A change
  owned by another pair (e.g. `account.invoice`→`account.move` is 12→13, not 11→12;
  `openerp`→`odoo` is 9→10, not 11→12) must **not** be re-listed as a new break. Mis-attribution
  is the #1 error this forge guards against.
- Books: no text may cross the content right edge — `verify_pdf.py` enforces 0 overflow spans;
  tables use fixed page-width layout with wrapping chips/code (`overflow-wrap: anywhere`).
- Books: keep the house design system (`references/design-system.md`); strip publisher PII/branding
  on request via a sanitize pass over the model before rendering.
- Skills: `SKILL.md` frontmatter + progressive-disclosure `references/` + stdlib `scripts/`;
  scanner exits 1 on findings (CI gate); every mapping row cites its reference anchor.
- Markdown: strict-renderer safe — run `check_markdown.py` (0 issues) after `normalize_markdown.py`.
- Every artifact ships a provenance appendix: branches/files/commands and the date checked.
- **Scanner smoke test (per skill):** build a minimal addon that exercises every PATTERNS
  entry, run `scan_addon.py`; it MUST exit 1 with **all** pattern ids hit (none silently
  missed). A clean addon (no patterns present) MUST exit 0. This is the skill's CI gate.
- **Bidirectional consistency (per pair):** after edits, run the pair's
  `check_cookbook_consistency.py` — the Cookbook and `references/` must cover each other's
  core change tokens with zero drift. This catches Skill/Cookbook divergence.

## Intermediate artifact archive (work/{version}/)

Keep each pair's research & QA assets under **`work/{version}/`** (e.g. `work/18to19/`)
so later revisions (confirm `[verify]` items, extend content, render PDF) reuse them
instead of re-deriving. At minimum archive three (see `references/intermediate-archive.md`):

- `RESEARCH_SOURCES.md` — official Changelog PR map + which community source proved which
  change + CE/EE verification entry points.
- `VERIFY_TRACKER.md` — per-item `[verify]`/`[EE-verify]` status, action and progress; on
  confirmation, remove the flag from **both** the Cookbook and `references/`.
- a consistency script (e.g. `check_cookbook_consistency.py`) — run after edits to prove the
  Cookbook and `references/` cover each other's core change tokens (no drift).

## Quality gates (per version pair)

**Cookbook (artifact 1)** — single volume; covers the X→Y breaking surface
(background + Before/After + source + verify status); version-scope verified
(no pre-X.0 or non-X→Y rows); `[verify]`/`[EE-verify]` flagged; ships a provenance
appendix; `verify_pdf.py` ⇒ 0 overflow spans (if rendered).

**Skill (artifact 2)** — `references/` covers the same surface (topics/files as needed,
not a fixed set); every row carries a provenance anchor; `[verify]`/`[EE-verify]` match the
Cookbook; `upgrade_code` list names only scripts that actually fire for `--to Y.0`;
`check_markdown.py` ⇒ 0 issues; scanner clean-addon ⇒ exit 0; SKILL.md frontmatter
parses as YAML; consistency script ⇒ Cookbook ↔ `references/` no drift.

## Worked examples (this forge's output)

- **15 version pairs, 5.0 → 20.0** — each ships the two-artifact contract (Cookbook +
  `OdooXXtoYYMigration/` skill with 6 references + scanner): `Odoo_Migration_Cookbook_*_to_*.md`
  plus `Odoo5to6Migration/` … `Odoo19to20Migration/`. Pairs ≤17 are **pure-hand** (no
  `upgrade_code`); 18→20 ship codemods (see `references/odoo-version-pairs.md`).
- `Odoo_Migration_Cookbook_19_to_20_fixed.pdf` — pipeline A (45 clipped spans restored).
- `Odoo_Migration_Cookbook_19_to_20_Vol2_Closing_the_Gaps.pdf` — pipelines B+C (8 chapters).
- `Odoo19to20Migration/` — pipeline D (skill with 6 references + scanner).
- `Core_Models_Changelog.md` + `scripts/diff_core_models.py` — pipeline G: the cross-version
  core-model index (5→20) and its model/field diff tool.

### Codemod reality (settles the hand-vs-automated split)

`odoo-bin upgrade_code` exists only in the **18.0+** tree. Therefore:

- **5 → 17: pure hand** — every break is a manual mapping row / OpenUpgrade script; the
  skill ships a `manual` scanner with no `auto` patterns.
- **18 → 20: codemod-assisted** — run `upgrade_code` from the *target* branch; `auto`
  scanner patterns mirror the firing codemod scripts (version-stamped prefixes).
- Forging a pair ≤17: do **not** invent `auto` patterns; mark all PATTERNS `manual`.
