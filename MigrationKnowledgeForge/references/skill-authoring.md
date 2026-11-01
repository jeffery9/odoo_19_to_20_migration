# Pipeline D — authoring a migration agent skill

## Layout (house convention, plugin-compatible)

```
<SkillName>/
├── SKILL.md          # frontmatter + Goal/Sources/Workflow/Hard rules
├── README.md         # install + use + QA
├── references/       # progressive disclosure: one md per topic, tables with provenance
└── scripts/          # stdlib only; scanner exit-code 1 = findings (CI gate)
```

Scaffold with `scripts/skill_scaffold.py` (copies the markdown QA scripts too).

## SKILL.md frontmatter

`name` (snake), `description` (starts with the job, lists trigger phrases and
concrete APIs so retrieval hits), `version`, `author`, `category: migration`,
`odoo_versions`/product versions, `tags`. Body stays ≤ ~60 lines: workflow steps
point into `references/`, never duplicate them.

## Description writing rules

- Include the version pair and 5–8 greppable API names (retrieval anchors).
- State the action verbs: migrate, fix, run codemods, validate, review diffs.

## References

- One topic per file; tables carry a **provenance column** (`src` cites the tree
  file, `doc`, `rec`, `EE`).
- Cross-link rows to sibling skills/volumes instead of copying them.
- Markdown strictness: after editing, run
  `python3 scripts/normalize_markdown.py references/*.md SKILL.md README.md`
  then `python3 scripts/check_markdown.py …` → 0 issues.
  (Rules: blank line at every block boundary; `\|` inside code spans in tables;
  no raw HTML-looking tags outside code; balanced fences; consistent columns.)

## Scanner design

- PATTERNS rows: `(id, extensions, regex, mode auto|manual, fix text, reference)`.
- Report groups by file with line numbers; summary splits auto (codemod) vs manual;
  `--json` for machines; exit 1 on findings.
- Deduplicate per (id, line); keep regexes single-line-tolerant for calls with
  nested parens (`read_group\([^\n]*?lazy\s*=`).

## QA gate before shipping

1. `check_markdown.py` → 0. 2. scanner on a deliberately-broken demo addon → all
   seeded patterns hit. 3. scanner on a clean addon → exit 0. 4. SKILL.md
   frontmatter parses as YAML.

## Version-specific notes & big jumps

- Flag version-pair-specific facts prominently in SKILL.md Hard rules (e.g. "security ACL
  CSV format changes only at 19→20; 18→19 keeps `ir.model.access.csv` with `perm_*`").
- A large frontend framework jump (Owl/QWeb) is usually the highest-effort area — give it
  its own reference file / chapter and call it out early.
- Record the runtime floor (Python / PostgreSQL minimum) for the target version.
- The Skill is the Cookbook's executable compression: keep `references/` fact-aligned to the
  Cookbook and run the pair's consistency script (see `intermediate-archive.md`) so the two
  never drift.
