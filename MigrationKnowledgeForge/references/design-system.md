# House design system (cookbook PDFs)

Page A4 portrait 595×842pt; page margins 57/50/45/50.2pt; a fixed beige panel
(`#f6f1e7`, border `#d8cfc0`) sits at 33.8/39.8pt sized 527.4×757.4pt behind the
flow (WeasyPrint repeats `position: fixed` per page; offset the panel by
`-margin` because the fixed containing block is the page area).

| Token | Value | Use |
|---|---|---|
| serif | Libre Baskerville | body 12.8pt/1.7 `#241c14` |
| mono | IBM Plex Mono | chips/code 9.8pt |
| ink | `#241c14` | body text |
| navy | `#1c2a3a` | chapter titles, table headers (`#f4eed6` on it) |
| gold | `#8b6914` | rules, h3 smallcaps, code-block left bar, TOC numbers |
| code bg | `#121c28` | code blocks, text `#f0e7d2` |
| chip bg | `#f3eee4` | inline code chips |
| row stripe | `#efe7d6` on `#fffdf8` | table even rows / wrapper |
| table border | `#c9b89a` 0.75pt | cell borders |

Blocks: chapter `h1` 24pt navy + gold rule 48×1.5pt + mono letterspaced
`BACK TO CONTENTS` link; `h2` bold 12.8; `h3.gold` 11.2 uppercase letterspaced;
bullets with `•` absolute marker; `hr` 0.7pt `#d8cfc0`.

Anti-clipping rules (mandatory):

- `table { table-layout: fixed; width: 100% }` + `<colgroup>` percentages taken
  from the original column ratios, normalized.
- chips & `pre.code`: `overflow-wrap: anywhere`; `pre` keeps `white-space: pre-wrap`.
- `tr, li, pre, h1..h3 { break-inside: avoid }`; `thead` repeats across pages.

Cover: full-panel dark gradient (`#0e1720 → #253443`), gold rule, 27pt cream
title lines, italic gold subtitle, mono letterspaced edition line, bottom block
(authors/notes) pinned by fixed margin. TOC: gold number column 55pt + ruled entries.

Fonts must be installed for WeasyPrint (fontconfig): Libre Baskerville (variable
ttf) + IBM Plex Mono; register via `/usr/local/share/fonts` + `fc-cache`.
