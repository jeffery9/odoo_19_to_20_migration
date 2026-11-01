# Odoo17to18Migration — agent skill

An agent skill (Claude/agent-skills `SKILL.md` format, compatible with the
`odoo-agent-pro-kit` plugin layout) for migrating custom Odoo **17.0** addons
to **18.0**, CE and EE.

This is the **17→18** member of the multi-version migration workspace
(see the root `../README.md`). The 18→19 member lives in
`../Odoo18to19Migration/`.

## Contents

```
Odoo17to18Migration/
├── SKILL.md                      # frontmatter + workflow + hard rules (17→18)
├── references/                   # progressive-disclosure tables (source-verified)
│   ├── views-qweb.md             # tree→list, colors→decoration, tree_view_ref→list_view_ref, kanban-box[verify], states[verify], fields_view_get[verify]
│   ├── orm-api.md                # name_get/_name_search/check_access/user_has_groups/check_recursion removals, aggregator, inselect, env._(), search_fetch
│   ├── http-rpc-mail.md          # type='json'→jsonrpc (18.1), translations, mail/binary stable, longpolling→ws
│   ├── security.md               # security file & res.groups UNCHANGED in 17→18 (vs 18→19/19→20)
│   ├── modules-mapping.md        # framework-level rename table + symptom index
│   └── upgrade-code.md           # odoo-bin upgrade_code usage + 17.5-01-tree-to-list only
└── scripts/
    ├── scan_addon.py             # stdlib scanner, CI-friendly exit code (version-agnostic, 17→18 patterns)
    ├── check_markdown.py         # markdown compatibility linter for these docs
    └── normalize_markdown.py     # inserts missing blank lines at block boundaries
```

## Install

- **odoo-agent-pro-kit plugin**: copy the folder into `plugin/skills/`
  (`plugin/skills/Odoo17to18Migration/`).
- **Claude Code / generic agent skills**: copy into your skills directory
  (e.g. `~/.claude/skills/`) or reference the folder in your plugin manifest.
- No dependencies: the scanner is Python stdlib; the skill itself is markdown.

## Use

1. Triage an addons tree:
   `python3 Odoo17to18Migration/scripts/scan_addon.py /path/to/addons`
   (`--addon my_module`, `--json`, `--quiet`; exit 1 = findings).
2. Ask the agent: *"migrate addon `my_module` from 17 to 18 using the
   odoo_17_to_18_migration skill"* — the skill drives: scan → codemod
   (`odoo-bin upgrade_code --from 17.0`) → manual mappings from `references/`
   → validate (`-u` + tests) → report.

## Scope & provenance

- Covers the **17.0 → 18.0** jump only (including 18.x Online minors new
  relative to 17). Items that changed *before* 18 (e.g. `aggregator` rename in
  17.2) appear only where still relevant to cleaning up 17 code — never as if
  new in 18.
- Tables are condensed from the Odoo ORM Changelog (odoo.com 18.0 docs, with PR
  numbers), the 18.0 source tree (verified `ir_ui_view.py` / `models.py` /
  `upgrade_code/`), and cross-checked community 17→18 upgrade write-ups (OCA
  maintainer-tools, Cybrosys, ODIWARE, DeployMonkey). Rows still needing source
  confirmation are tagged **[verify]**; Enterprise-only rows are tagged
  **[EE-verify]** and must be re-checked against the Enterprise 18.0 tree.
- **Codemod reality:** 17→18 ships only ONE bundled codemod (`17.5-01-tree-to-list`,
  `tree`→`list`). All other removals/renames (`name_get`, `check_access_rights`,
  `user_has_groups`, `group_operator`→`aggregator`, `type='json'`→`jsonrpc`) have
  **no codemod** in the 17→18 flow — they are manual.
