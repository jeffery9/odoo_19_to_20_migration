#!/usr/bin/env python3
"""Book factory: house design system + HTML emitters + WeasyPrint render.

Used by pipeline A/C of the migration_knowledge_forge meta-skill.
Content model: runs are (kind, text) tuples:
  t plain · c code chip · b bold · i italic · cb bold chip
Cells are lists of lines; each line is a list of runs.
"""
import html as _html

CSS = """@page { size: 595pt 842pt; margin: 57pt 50pt 45pt 50.2pt; }
* { box-sizing: border-box; }
body { font-family: 'Libre Baskerville', serif; font-size: 12.8pt; color: #241c14; line-height: 1.7; }
.panel { position: fixed; top: -17.2pt; left: -16.4pt; width: 527.4pt; height: 757.4pt;
         background: #f6f1e7; border: 0.7pt solid #d8cfc0; z-index: -1; }
.pb, h1.ch, .toc-title { break-before: page; }
h1 { font-weight: 400; color: #1c2a3a; margin: 0 0 4pt; line-height: 1.2; }
h1.ch { margin-top: 42pt; }
h1.ch::after { content: ''; display: block; width: 48pt; height: 1.5pt; background: #8b6914; margin: 12pt 0 0; }
h1.cover { color: #241c14; margin: 6pt 0; }
.toc-title { color: #1c2a3a; font-weight: 700; margin-top: 40pt; }
a { color: inherit; }
a.back { display: block; font-family: 'IBM Plex Mono', monospace; font-size: 9pt; color: #5a4c42;
         letter-spacing: 1.1pt; text-decoration: none; margin: 10pt 0 16pt; }
a.toc-entry { display: block; text-decoration: none; margin: 0 0 7pt; }
h2 { font-size: 12.8pt; font-weight: 700; margin: 16pt 0 8pt; color: #241c14; }
h3.gold { font-size: 11.2pt; font-weight: 700; color: #8b6914; letter-spacing: .8pt;
          text-transform: uppercase; margin: 16pt 0 7pt; }
p { margin: 0 0 10pt; }
.b { font-weight: 700; } .i { font-style: italic; }
.chip { font-family: 'IBM Plex Mono', monospace; font-size: 9.8pt; background: #f3eee4;
        padding: 1.2pt 4pt; border-radius: 2.5pt; overflow-wrap: anywhere; }
.mono { font-family: 'IBM Plex Mono', monospace; }
pre.code { font-family: 'IBM Plex Mono', monospace; font-size: 9.8pt; line-height: 1.62; color: #f0e7d2;
           background: #121c28; border-left: 2.3pt solid #8b6914; padding: 11pt 16pt; margin: 10pt 0;
           white-space: pre-wrap; overflow-wrap: anywhere; }
pre.code .cr { font-family: inherit; }
table { border-collapse: collapse; width: 100%; table-layout: fixed; background: #fffdf8; margin: 12pt 0; }
th, td { border: 0.75pt solid #c9b89a; padding: 6.5pt 9pt; vertical-align: top; font-size: 9.8pt;
         line-height: 1.55; text-align: left; font-weight: 400; }
th { background: #1c2a3a; color: #f4eed6; font-family: 'IBM Plex Mono', monospace; font-weight: 700; }
tbody tr:nth-child(even) td { background: #efe7d6; }
td.note { font-size: 9.8pt; }
td .chip, th .chip { font-size: 9.8pt; }
ul.bullets { list-style: none; margin: 8pt 0 10pt; padding: 0; }
ul.bullets li { position: relative; padding-left: 16.5pt; margin: 0 0 7pt; }
ul.bullets li::before { content: '\2022'; position: absolute; left: 2pt; color: #241c14; }
hr { border: 0; border-top: 0.7pt solid #d8cfc0; margin: 16pt 0; }
tr, li, pre.code, h1, h2, h3 { break-inside: avoid; }
thead { break-inside: avoid; }
h1.sub { color: #1c2a3a; font-weight: 700; margin: 18pt 0 8pt; }
.toc-title { color: #241c14 !important; }
a.toc-entry { display: block; text-decoration: none; border-bottom: 0.7pt solid #d8cfc0;
              padding: 8.5pt 0 8pt; margin: 0; }
.tocnum { display: inline-block; width: 55pt; }
div.coverpage { margin: -17.2pt -16.4pt 0; height: 757.4pt; padding: 42pt 44pt 40pt;
                background: linear-gradient(150deg, #0e1720 0%, #16212e 55%, #253443 100%);
                break-after: page; color: #f0e7d2; }
div.coverpage .cover-mono { font-family: 'IBM Plex Mono', monospace; font-size: 9pt;
        letter-spacing: 1.6pt; color: #c8bba8; margin: 0 0 4pt; }
div.coverpage .cover-title { color: #fdf6e9; font-weight: 400; line-height: 1.3; margin: 0; }
.cover-rule + .cover-title { margin-top: 26pt; }
div.coverpage .cover-sub { color: #e5c987; font-style: italic; margin: 14pt 0 0; }
div.coverpage .cover-line { margin: 0 0 7pt; color: #f0e7d2; }
div.coverpage .cover-line .cr { color: #e5c987; }
.cover-rule { width: 90pt; height: 1.5pt; background: #8b6914; margin: 18pt 0 0; }
.cover-bottom { margin-top: 330pt; }
.cover-bottom .cover-line { margin: 0 0 8pt; }"""


def esc(t):
    return _html.escape(t, quote=False)


_SEG = {'t': '', 'c': 'chip', 'b': 'b', 'i': 'i', 'cb': 'chip b'}


class Book:
    def __init__(self, title):
        self.title = title
        self.out = []

    def _runs(self, segs, default=12.8):
        parts = []
        for kind, txt in segs:
            cls = _SEG[kind]
            style = 'font-size:9.8pt' if kind in ('c', 'cb') and default > 10 else ''
            attr = ''
            if cls:
                attr += ' class="%s"' % cls
            if style:
                attr += ' style="%s"' % style
            parts.append('<span%s>%s</span>' % (attr, esc(txt)))
        return ''.join(parts)

    def _cell(self, lines, default=9.8):
        return '<br/>'.join(self._runs(ln, default) for ln in lines)

    def cover(self, title_lines, subtitle, edition, bottom=()):
        s = ['<div class="coverpage"><div class="cover-rule"></div>']
        for ln in title_lines:
            s.append('<div class="cover-title" style="font-size:27pt">%s</div>' % esc(ln))
        s.append('<div class="cover-sub" style="font-size:16.5pt">%s</div>' % esc(subtitle))
        s.append('<div class="cover-mono">%s</div>' % esc(edition))
        if bottom:
            s.append('<div class="cover-bottom">%s</div>'
                     % ''.join('<div class="cover-line">%s</div>' % esc(b) for b in bottom))
        s.append('</div>')
        self.out.append(''.join(s))

    def page_break(self):
        self.out.append('<div class="pb"></div>')

    def toc(self, entries, note='Select a chapter to open it.'):
        self.out.append('<h1 class="toc-title pb" id="contents" style="font-size:25.5pt">Contents</h1>')
        self.p([('t', note)])
        for num, name in entries:
            self.out.append('<a class="toc-entry" href="#ch-%d"><span class="tocnum">%d.</span>%s</a>'
                            % (num, num, esc(name)))

    def chapter(self, num, title):
        self.out.append('<h1 class="ch pb" id="ch-%d">%s</h1>' % (num, esc(title)))

    def back(self):
        self.out.append('<a class="back" href="#contents">BACK TO CONTENTS</a>')

    def h2(self, text_or_segs):
        segs = text_or_segs if isinstance(text_or_segs, list) else [('b', text_or_segs)]
        self.out.append('<h2>%s</h2>' % self._runs(segs))

    def h3gold(self, text):
        self.out.append('<h3 class="gold">%s</h3>' % esc(text))

    def p(self, segs):
        self.out.append('<p>%s</p>' % self._runs(segs))

    def bul(self, segs):
        self.out.append('<ul class="bullets"><li>%s</li></ul>' % self._runs(segs))

    def code(self, lines):
        self.out.append('<pre class="code">%s</pre>' % '\n'.join(esc(l) for l in lines))

    def table(self, headers, rows, widths=None):
        n = len(headers)
        ws = widths or [100.0 / n] * n
        s = ['<table><colgroup>'] + ['<col style="width:%.2f%%"/>' % w for w in ws]
        s.append('</colgroup><thead><tr>')
        s += ['<th>%s</th>' % esc(h) for h in headers]
        s.append('</tr></thead><tbody>')
        for r in rows:
            s.append('<tr>')
            s += ['<td>%s</td>' % self._cell([c] if (c and isinstance(c[0], tuple)) else c) for c in r]
            s.append('</tr>')
        s.append('</tbody></table>')
        self.out.append(''.join(s))

    def hr(self):
        self.out.append('<hr/>')

    def html(self):
        return ('<!DOCTYPE html><html><head><meta charset="utf-8"/>\n<title>%s</title>\n'
                '<style>%s</style></head><body>\n<div class="panel"></div>\n%s\n</body></html>'
                % (esc(self.title), CSS, '\n'.join(self.out)))

    def write_html(self, path):
        open(path, 'w').write(self.html())
        return path

    def write_pdf(self, html_path, pdf_path):
        from weasyprint import HTML
        HTML(html_path).write_pdf(pdf_path)
        return pdf_path


T = lambda t: ('t', t)
C = lambda t: ('c', t)
B = lambda t: ('b', t)
I = lambda t: ('i', t)
