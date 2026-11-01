# Odoo18to19Migration — agent skill

An agent skill (Claude/agent-skills `SKILL.md` format, compatible with the
`odoo-agent-pro-kit` plugin layout) for migrating custom Odoo **18.0** addons
to **19.0**, CE and EE.

This is the **18→19** member of the multi-version migration workspace
(see the root [`README.md`](../README.md)). The 19→20 member lives in
`../Odoo19to20Migration/`.

## Contents

```
Odoo18to19Migration/
├── SKILL.md                      # frontmatter + workflow + hard rules (18→19)
├── references/                   # progressive-disclosure tables (source-verified)
│   ├── security-and-orm.md       # ir.model.access UNCHANGED; res.groups; ORM/import renames
│   ├── binary-http-mail.md       # type='json'→jsonrpc, RPC deprecation, mail/SQL
│   ├── views-qweb-owl.md         # Owl 2→3, kanban card, view strictness, action targets
│   ├── modules-mapping.md        # module/model/field renames + symptom index
│   ├── api-deltas-vol2.md        # runtime/imports, cache & SQL, model API, fields, tests
│   └── upgrade-code.md           # odoo-bin upgrade_code usage + script contract
└── scripts/
    ├── scan_addon.py             # stdlib scanner, CI-friendly exit code (version-agnostic)
    ├── check_markdown.py         # markdown compatibility linter for these docs
    └── normalize_markdown.py     # inserts missing blank lines at block boundaries
```

## Install

- **odoo-agent-pro-kit plugin**: copy the folder into `plugin/skills/`
  (`plugin/skills/Odoo18to19Migration/`).
- **Claude Code / generic agent skills**: copy into your skills directory
  (e.g. `~/.claude/skills/`) or reference the folder in your plugin manifest.
- No dependencies: the scanner is Python stdlib; the skill itself is markdown.

## Use

1. Triage an addons tree:
   `python3 Odoo18to19Migration/scripts/scan_addon.py /path/to/addons`
   (`--addon my_module`, `--json`, `--quiet`; exit 1 = findings).
2. Ask the agent: *"migrate addon `my_module` from 18 to 19 using the
   odoo_18_to_19_migration skill"* — the skill drives: scan → codemod
   (`odoo-bin upgrade_code --from 18.0`) → manual mappings from `references/`
   → validate (`-u` + tests) → report.

## Scope & provenance

- Covers the **18.0 → 19.0** jump only. Items that changed *before* 19 (e.g.
  `aggregator` rename in 17.2, `Domain` API in 18.1, `type='json'`→`jsonrpc` in
  18.1, `check_access`/`has_access` in 18.0) appear only where still relevant to
  cleaning up 18 code — never as if new in 19.
- Tables are condensed from the Odoo ORM Changelog (odoo.com 19.0 docs) and
  cross-checked community 18→19 upgrade write-ups. Rows still needing source
  confirmation are tagged **[verify]**; Enterprise-only rows are tagged
  **[EE-verify]** and must be re-checked against the Enterprise 19.0 tree.
