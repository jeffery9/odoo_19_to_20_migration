# Odoo19to20Migration — agent skill

An agent skill (Claude/agent-skills `SKILL.md` format, compatible with the
`odoo-agent-pro-kit` plugin layout) for migrating custom Odoo **19.0** addons
to **20.0**, CE and EE.

## Contents
```
Odoo19to20Migration/
├── SKILL.md                      # frontmatter + workflow + hard rules
├── references/                   # progressive-disclosure tables (source-verified)
│   ├── security-and-orm.md       # ir.access.csv, ORM renames, domains/read_group
│   ├── binary-http-mail.md       # binary/Excel/PDF/time, routes, mail, SQL reports
│   ├── views-qweb-owl.md         # view xpaths, ribbons/icons, kanban cards, Owl 3
│   ├── modules-mapping.md        # per-module model/field/xml-id maps + symptom index
│   ├── api-deltas-vol2.md        # runtime/imports, cache & SQL, model API, fields, tests
│   └── upgrade-code.md           # odoo-bin upgrade_code usage + script contract
└── scripts/
    └── scan_addon.py             # stdlib scanner, CI-friendly exit code
```

## Install
- **odoo-agent-pro-kit plugin**: copy the folder into `plugin/skills/`
  (`plugin/skills/Odoo19to20Migration/`).
- **Claude Code / generic agent skills**: copy into your skills directory
  (e.g. `~/.claude/skills/`) or reference the folder in your plugin manifest.
- No dependencies: the scanner is Python stdlib; the skill itself is markdown.

## Use
1. Triage an addons tree:
   `python3 Odoo19to20Migration/scripts/scan_addon.py /path/to/addons`
   (`--addon my_module`, `--json`, `--quiet`; exit 1 = findings).
2. Ask the agent: *"migrate addon `my_module` from 19 to 20 using the
   odoo_19_to_20_migration skill"* — the skill drives: scan → codemod
   (`odoo-bin upgrade_code --from 19.0`) → manual mappings from `references/`
   → validate (`-u` + tests) → report.

## Provenance
Tables are condensed from the companion cookbooks (Volume I fixed edition +
Volume II *Closing the Gaps*), whose entries were verified against the
`odoo/odoo` branches `19.0`/`20.0` on 2026-10-11. Enterprise-only rows carry
**[EE-verify]** and must be re-checked against the Enterprise 20.0 tree.
