# MigrationKnowledgeForge — meta-skill

Forges migration knowledge artifacts: repaired/rebuilt cookbook PDFs, new
cookbook volumes mined from two version branches, migration agent skills, and a
cross-version core-model changelog. It encapsulates the pipelines that produced the
Odoo **5.0 → 20.0** body of work — 15 version-pair cookbooks + skills (5→6 … 19→20,
pure-hand ≤17, codemod-assisted 18→20), the 19→20 Volume I (fixed) / Volume II
*Closing the Gaps*, and the `Core_Models_Changelog.md` index — parameterized so other
version pairs/products can reuse them.

**Product contract:** each version pair ships exactly **two** artifacts, in order —
a **Cookbook** (authored first, the source of truth) then a **Migration Skill**
(forged second, fact-aligned to the Cookbook). See `SKILL.md`.

## Contents

```
MigrationKnowledgeForge/
├── SKILL.md                        # meta-skill: pipelines, provenance hierarchy, hard rules
├── README.md
├── references/
│   ├── cookbook-pipeline.md        # A: clipped-PDF repair → model → completion → render → verify
│   ├── source-diff-mining.md       # B: two-ref diff mining + S1–S6 research ranking
│   ├── skill-authoring.md          # D: skill layout, frontmatter, references, scanner, QA
│   ├── design-system.md            # C: house CSS tokens & anti-clipping rules
│   ├── odoo-version-pairs.md       # F: verified matrix + presets + version-scope discipline
│   ├── version-scope-redlines.md   # G: canonical 5→20 change-ownership table (anti mis-attribution)
│   ├── cross-version-models.md     # G: cross-version core-model index pattern + diff tool
│   └── intermediate-archive.md     # work/<version>/ convention: research map, verify tracker, consistency script
└── scripts/
    ├── pdf_extract.py              # PDF → model.json (geometry-driven, clip detection)
    ├── booklib.py                  # design system + HTML emitters + WeasyPrint render
    ├── verify_pdf.py               # overflow-span + required-string QA gate
    ├── branch_diff.py              # defs/classes/exports/grep diffs between two refs
    ├── skill_scaffold.py           # new skill folder skeleton (+ QA scripts copied in)
    ├── check_markdown.py           # markdown compatibility linter (strict renderers)
    ├── normalize_markdown.py       # blank-line boundary normalizer (idempotent)
    └── diff_core_models.py         # G: model/field-level cross-version diff (branch_diff specialisation)
```

## Install & use

Copy the folder into your skills/plugins directory. Typical invocations:

```bash
python3 scripts/pdf_extract.py --pdf broken.pdf --out model.json
python3 scripts/branch_diff.py --repo odoo/odoo --a 19.0 --b 20.0 --pairs "odoo/tools/__init__.py" --kind exports
python3 scripts/diff_core_models.py --repo /path/to/odoo --ref-a 19.0 --ref-b 20.0 --model res.partner   # local git, no network
python3 scripts/skill_scaffold.py --dir ./NewSkill --name new_migration --title "New 1→2" --description "…"
python3 scripts/verify_pdf.py --pdf book.pdf --must-file completed.txt
python3 scripts/check_markdown.py SKILL.md references/*.md
```

Python deps for rendering: `pymupdf`, `weasyprint`; system deps (Debian):
`apt-get install libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libharfbuzz-subset0 fontconfig`
plus the house fonts (Libre Baskerville, IBM Plex Mono) via `fc-cache` — see
`references/design-system.md`. All other scripts are stdlib.

## Provenance & honesty rules

Completed values record their tier (corpus doc / public source / reconstruction);
vendor-private items stay **[EE-verify]**. Books ship a verification appendix;
skills carry a provenance column per mapping row.
