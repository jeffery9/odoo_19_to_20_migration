#!/usr/bin/env python3
"""Generate fixed PDF (no clipped tables) from the extracted document model."""
import json, html

m = json.load(open('work/model.json'))
pages = m['pages']

BODY = '#241c14'

def esc(t):
    return html.escape(t, quote=False)

def run_html(r, default_size, in_code=False, in_th=False):
    txt = esc(r['text'])
    if not txt:
        return ''
    cls = []
    if r.get('mono') and not in_code:
        cls.append('chip' if not in_th else 'mono')
    elif r.get('mono') and in_code:
        cls.append('cr')
    if r.get('bold'):
        cls.append('b')
    if r.get('italic'):
        cls.append('i')
    st = []
    if r.get('color') and r['color'] != BODY and not in_code:
        st.append('color:%s' % r['color'])
    if in_code and r.get('color') and r['color'] != '#f0e7d2':
        st.append('color:%s' % r['color'])
    if abs(r.get('size', default_size) - default_size) > 0.05:
        st.append('font-size:%spt' % r['size'])
    attr = ''
    if cls:
        attr += ' class="%s"' % ' '.join(cls)
    if st:
        attr += ' style="%s"' % ';'.join(st)
    return '<span%s>%s</span>' % (attr, txt)

def lines_html(cell, default_size, in_th=False):
    out = []
    for ln in cell['lines']:
        out.append(''.join(run_html(r, default_size, in_th=in_th) for r in ln))
    return '<br/>'.join(out) if out else ''


# ---------- sanitize: remove Probuse Consulting Service Pvt. Ltd. information ----------
DROP_KW = ['probuse', 'contact@probuse', 'ahmedabad', 'sakarix', 'ashramroad', 'telephone:+91',
           'middleeastandgcccontact', 'europecontact:', 'publishedby', 'aboutthepublisher',
           'copyright\u00a92026', 'copyright©2026']
def block_text(b):
    if b['t'] == 'h1':
        return b['text']
    return ''.join(r['text'] for r in b.get('runs', []))

def is_names_only(t):
    n = t.replace(' ', '')
    return n in ('Mr.MustufaRangwalaMs.SananazMansuri', 'Mr.MustufaRangwalaandMs.SananazMansuri')

# rewrite author bios (remove company affiliation sentences)
for pg in pages:
    for b in pg['blocks']:
        t = block_text(b)
        if t.startswith('Mr. Mustufa Rangwala is Founder'):
            b['runs'] = [
                {'text': 'Mr. Mustufa Rangwala', 'size': 12.8, 'mono': False, 'bold': True, 'italic': False, 'color': '#241c14', 'x1': 0},
                {'text': ' has worked in the Odoo / OpenERP ecosystem since the early versions and previously worked with Odoo India.', 'size': 12.8, 'mono': False, 'bold': False, 'italic': False, 'color': '#241c14', 'x1': 0}]
        elif t.startswith('Ms. Sananaz Mansuri is a Consultant'):
            b['runs'] = [
                {'text': 'Ms. Sananaz Mansuri', 'size': 12.8, 'mono': False, 'bold': True, 'italic': False, 'color': '#241c14', 'x1': 0},
                {'text': ' is a Consultant and Odoo techno-functional implementer. She works on requirement analysis, process mapping, configuration, and delivery.', 'size': 12.8, 'mono': False, 'bold': False, 'italic': False, 'color': '#241c14', 'x1': 0}]

for pg in pages:
    keep = []
    for b in pg['blocks']:
        t = block_text(b)
        norm = t.lower().replace(' ', '').replace('\n', '')
        if not is_names_only(t) and any(k in norm for k in DROP_KW):
            continue
        keep.append(b)
    pg['blocks'] = keep
# merge wrapped chapter titles (consecutive h1 on same page)
for pg in pages:
    bs = pg['blocks']
    for i in range(len(bs)-1, 0, -1):
        if bs[i]['t'] == 'h1' and bs[i-1]['t'] == 'h1' and bs[i].get('size') == 24.0 and bs[i-1].get('size') == 24.0:
            bs[i-1]['text'] = bs[i-1]['text'] + ' ' + bs[i]['text']
            bs.pop(i)

out = []
chapter = 0
out.append('<div class="panel"></div>')
FRONT_BREAK_PAGES = {2, 3}

def cover_html(pg):
    s = ['<div class="coverpage">']
    title_seen = False
    bottom = []
    for b in pg['blocks']:
        if b['t'] == 'h1':
            if not title_seen:
                s.append('<div class="cover-rule"></div>')
                title_seen = True
            cls = 'cover-title' if b.get('size', 0) >= 26 else 'cover-sub'
            s.append('<div class="%s" style="font-size:%spt">%s</div>' % (cls, b.get('size', 27), esc(b['text'])))
        else:
            runs = b['runs']
            mono = all(r.get('mono') for r in runs if r['text'].strip())
            txt = ''.join(r['text'] for r in runs)
            if 'Rangwala' in txt or 'Mansuri' in txt:
                for part in ['Mr. Mustufa Rangwala', 'Ms. Sananaz Mansuri']:
                    if part in txt:
                        bottom.append('<div class="cover-line">%s</div>' % part)
            elif mono:
                s.append('<div class="cover-mono">%s</div>' % ''.join(run_html(r, 9.0, in_code=True) for r in runs))
            else:
                s.append('<div class="cover-line">%s</div>' % lines_html({'lines': [runs]}, 12.0))
    if bottom:
        s.append('<div class="cover-bottom">%s</div>' % ''.join(bottom))
    s.append('</div>')
    return s

for pno, pg in enumerate(pages):
    blocks = pg['blocks']
    if pno == 0:
        out.extend(cover_html(pg))
        continue
    first = True
    i = 0
    while i < len(blocks):
        b = blocks[i]
        pb = ''
        if first and pno in FRONT_BREAK_PAGES:
            pb = ' pb'
        first = False
        t = b['t']
        if t == 'h1':
            size = b.get('size', 24.0)
            if size == 24.0 and pno >= 4:
                chapter += 1
                out.append('<h1 class="ch pb" id="ch-%d" style="font-size:%spt">%s</h1>' % (chapter, size, esc(b['text'])))
            elif pno == 3:
                out.append('<h1 id="contents" class="toc-title%s" style="font-size:%spt">%s</h1>' % (pb, size, esc(b['text'])))
            elif abs(size - 19.5) < 0.1:
                out.append('<h1 class="sub%s" style="font-size:%spt">%s</h1>' % (pb, size, esc(b['text'])))
            else:
                out.append('<h1 class="cover%s" style="font-size:%spt">%s</h1>' % (pb, size, esc(b['text'])))
        elif t == 'back':
            out.append('<a class="back%s" href="#contents">BACK TO CONTENTS</a>' % pb)
        elif t == 'h2':
            out.append('<h2 class="%s">%s</h2>' % (pb.strip() or 'x', lines_html({'lines': [b['runs']]}, 12.8)))
        elif t == 'code':
            inner = '\n'.join(''.join(run_html(r, 9.8, in_code=True) for r in ln) for ln in b['lines'])
            out.append('<pre class="code%s">%s</pre>' % (pb, inner))
        elif t == 'table':
            cols = b['cols']
            cx = b['col_x']
            total = cx[-1] - cx[0]
            widths = [(cx[k+1]-cx[k]) / total * 100 for k in range(cols)]
            s = ['<table class="%s"><colgroup>' % pb.strip()]
            for w in widths:
                s.append('<col style="width:%.2f%%"/>' % w)
            s.append('</colgroup>')
            if b['header']:
                s.append('<thead><tr>')
                for c in b['header']:
                    s.append('<th>%s</th>' % lines_html(c, 9.8, in_th=True))
                s.append('</tr></thead>')
            s.append('<tbody>')
            for row in b['rows']:
                nonempty = [c for c in row if lines_html(c, 9.8).strip()]
                s.append('<tr>')
                if len(nonempty) <= 1 and cols > 1:
                    c = nonempty[0] if nonempty else row[0]
                    s.append('<td colspan="%d" class="note">%s</td>' % (cols, lines_html(c, 9.8)))
                else:
                    for c in row:
                        s.append('<td>%s</td>' % lines_html(c, 9.8))
                s.append('</tr>')
            s.append('</tbody></table>')
            out.append(''.join(s))
        elif t == 'bul':
            items = []
            while i < len(blocks) and blocks[i]['t'] == 'bul':
                items.append('<li>%s</li>' % lines_html({'lines': [blocks[i]['runs']]}, 12.8))
                i += 1
            out.append('<ul class="bullets%s">%s</ul>' % (pb, ''.join(items)))
            continue
        elif t == 'hr':
            out.append('<hr/>')
        elif t == 'p':
            runs = b['runs']
            txt = ''.join(r['text'] for r in runs)
            allgold = all(r['color'] == '#8b6914' for r in runs if r['text'].strip()) and txt.strip()
            allbold = all(r.get('bold') for r in runs if r['text'].strip())
            if allgold and allbold and txt.strip() == txt.strip().upper():
                out.append('<h3 class="gold%s">%s</h3>' % (pb, lines_html({'lines': [runs]}, 11.2)))
            else:
                # TOC entry?
                if pno in (3, 4) and runs and runs[0].get('color') == '#8b6914':
                    num = runs[0]['text'].strip().rstrip('.')
                    if num.isdigit():
                        body = '<span class="tocnum">%s</span>%s' % (esc(runs[0]['text']), ''.join(run_html(r, 12.8) for r in runs[1:]))
                        out.append('<a class="toc-entry%s" href="#ch-%s">%s</a>' % (pb, num, body))
                        i += 1
                        continue
                out.append('<p class="%s">%s</p>' % (pb.strip() or 'x', lines_html({'lines': [runs]}, 12.8)))
        i += 1

html_doc = '''<!DOCTYPE html><html><head><meta charset="utf-8"/>
<title>Odoo Migration Cookbook — Version 19 to Version 20</title>
<style>
@page { size: 595pt 842pt; margin: 57pt 50pt 45pt 50.2pt; }
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
ul.bullets li::before { content: '\\2022'; position: absolute; left: 2pt; color: #241c14; }
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
.cover-bottom { margin-top: 372pt; }
.cover-bottom .cover-line { margin: 0 0 8pt; }
</style></head><body>
''' + '\n'.join(out) + '\n</body></html>'

open('work/book.html', 'w').write(html_doc)
print('html written, chapters:', chapter, 'bytes:', len(html_doc))
