# Intermediate artifact archive (work/{version}/)

When forging a version pair, keep its research & QA assets under **`work/<version>/`**
(e.g. `work/18to19/`) so later revisions — confirming `[verify]` items, extending content,
rendering a PDF — reuse them instead of re-deriving from scratch. This convention was
first proven on the 18→19 pair and is now part of the forge contract.

## What to archive (minimum three)

1. **`RESEARCH_SOURCES.md`** — the evidence map:
   - Official Changelog PR map (PR# → change, with the introducing version).
   - Which community source (Cybrosys / SDLC / LineScripts / DeployMonkey / ERP24 / Octura …)
     corroborated which change, so a single source is never treated as definitive.
   - CE / EE verification entry points (`odoo/odoo` `X.0` vs `Y.0` branch diff, EE tree).
2. **`VERIFY_TRACKER.md`** — the `[verify]` / `[EE-verify]` backlog:
   - one row per open item: claim, current evidence tier, action, status.
   - on confirmation, **remove the flag from both the Cookbook and `references/`** (never
     from only one — that is how the two artifacts drift).
3. **A consistency script** (e.g. `check_cookbook_consistency.py`):
   - enumerates the Cookbook and `references/` core change tokens; asserts each token is
     present on **both** sides (bidirectional coverage).
   - run it after every revision; a failure means the two artifacts have diverged.

## Workflow

- At pair start: `mkdir -p work/<version>/` and seed `RESEARCH_SOURCES.md` + `VERIFY_TRACKER.md`.
- During authoring: keep both files current; every `[verify]` you add goes into the tracker.
- On revision: resolve tracker rows → strip flags on both sides → run the consistency script.
- The archive is reusable across sessions; it is the pair's "memory" and should be committed
  alongside the Cookbook and Skill.
