#!/usr/bin/env python3
"""Extract structured document model from the Odoo migration cookbook PDF."""
import pymupdf, json
from collections import defaultdict

DOC = 'uploads/Odoo_Migration_Cookbook_19_to_20.pdf'
CLIP_X = 545.3

CODE_BG   = (0.071, 0.11, 0.157)
GOLD      = (0.545, 0.412, 0.078)
TBL_HEAD  = (0.11, 0.165, 0.228)
TBL_ROW   = (0.937, 0.902, 0.839)
TBL_WRAP  = (1.0, 0.992, 0.973)
BORDER    = (0.788, 0.722, 0.604)

STYLE = {
 'IBMPlexMono-Regular': {'mono': True},
 'Type3 (16 0 R)': {'mono': True, 'bold': True},
 'Type3 (17 0 R)': {'mono': True, 'bold': True},
 'Type3 (71 0 R)': {'mono': True, 'bold': True},
 'Type3 (13 0 R)': {'bold': True},
 'Type3 (6 0 R)': {},
 'Type3 (28 0 R)': {'bold': True},
 'Type3 (29 0 R)': {},
 'Type3 (121 0 R)': {'bold': True},
 'Type3 (63 0 R)': {'bold': True},
 'Type3 (5 0 R)': {'mono': True},
 'LiberationSerif': {},
 'LiberationSans-Bold': {'bold': True},
 'LibreBaskerville-Italic': {'italic': True},
}

def close(c, ref, tol=0.02):
    return c is not None and all(abs(a-b) <= tol for a, b in zip(c, ref))

def mk_run(s):
    st = STYLE.get(s['font'], {})
    return {'text': s['text'], 'size': round(s['size'], 1),
            'mono': st.get('mono', False), 'bold': st.get('bold', False),
            'italic': st.get('italic', False),
            'color': '#%06x' % s['color'], 'x1': round(s['bbox'][2], 1)}

doc = pymupdf.open(DOC)
model = {'pages': []}

for pno, page in enumerate(doc):
    fills = []
    strokes = []
    for d in page.get_drawings():
        r = d['rect']
        if d.get('fill') is not None:
            fills.append((tuple(round(c, 3) for c in d['fill']), r))
        if d.get('color') is not None:
            strokes.append((tuple(round(c, 3) for c in d['color']), r))

    code_rects = [r for c, r in fills if close(c, CODE_BG)]
    wrappers   = [r for c, r in fills if close(c, TBL_WRAP) and r.width > 100 and r.height > 20]
    head_rects = [r for c, r in fills if close(c, TBL_HEAD)]
    borders    = [r for c, r in fills if close(c, BORDER)]
    discs      = [r for c, r in fills if close(c, (0.141, 0.11, 0.078)) and r.width < 8 and r.height < 8]

    orig_lines = []   # (bbox, [spans])
    for b in page.get_text('dict')['blocks']:
        if 'lines' not in b: continue
        for l in b['lines']:
            sp = [s for s in l['spans']]
            if not sp: continue
            orig_lines.append((pymupdf.Rect(l['bbox']), sp))

    used = [False] * len(orig_lines)
    blocks = []

    def center_in(bb, r, pad=2.0):
        cx, cy = (bb.x0+bb.x1)/2, (bb.y0+bb.y1)/2
        return r.x0-pad <= cx <= r.x1+pad and r.y0-pad <= cy <= r.y1+pad

    # code blocks
    for cr in code_rects:
        lines = []
        for i, (bb, sp) in enumerate(orig_lines):
            if not used[i] and center_in(bb, cr):
                used[i] = True
                lines.append((bb.y0, [mk_run(s) for s in sorted(sp, key=lambda s: s['bbox'][0])]))
        lines.sort(key=lambda t: t[0])
        blocks.append({'t': 'code', 'y': cr.y0,
                       'lines': [r for _, r in lines],
                       'clipped': any(s['x1'] > CLIP_X for _, r in lines for s in r)})

    # tables
    for wr in wrappers:
        vbars = sorted({round(r.x0, 1) for r in borders
                        if r.width <= 1.6 and r.height > 5 and wr.x0-2 <= r.x0 <= wr.x1+2
                        and r.y0 >= wr.y0-2 and r.y1 <= wr.y1+2})
        hbars = sorted({round(r.y0, 1) for r in borders
                        if r.height <= 1.6 and r.width > 5 and wr.y0-2 <= r.y0 <= wr.y1+2
                        and r.x0 >= wr.x0-2 and r.x1 <= wr.x1+2})
        xs = [round(wr.x0, 1)] + vbars + [round(wr.x1, 1)]
        cols_x = []
        for x in xs:
            if not cols_x or x - cols_x[-1] > 3: cols_x.append(x)
        ys = [round(wr.y0, 1)] + hbars + [round(wr.y1, 1)]
        rows_y = []
        for y in ys:
            if not rows_y or y - rows_y[-1] > 3: rows_y.append(y)
        ncols, nrows = len(cols_x)-1, len(rows_y)-1
        if ncols < 1 or nrows < 1: continue
        grid = [[[] for _ in range(ncols)] for _ in range(nrows)]
        for i, (bb, sp) in enumerate(orig_lines):
            if used[i]: continue
            cx, cy = (bb.x0+bb.x1)/2, (bb.y0+bb.y1)/2
            if not (wr.x0-2 <= cx <= wr.x1+2 and wr.y0-2 <= cy <= wr.y1+2): continue
            ci = max(range(ncols), key=lambda c: cols_x[c] if cols_x[c] <= cx else -1e9)
            ri = max(range(nrows), key=lambda rr: rows_y[rr] if rows_y[rr] <= cy else -1e9)
            used[i] = True
            grid[ri][ci].append((bb.y0, [mk_run(s) for s in sorted(sp, key=lambda s: s['bbox'][0])]))
        rows = []
        for ri in range(nrows):
            cells = []
            for ci in range(ncols):
                ls = sorted(grid[ri][ci], key=lambda t: t[0])
                cells.append({'lines': [r for _, r in ls],
                              'clipped': any(s['x1'] > CLIP_X for _, r in ls for s in r)})
            rows.append(cells)
        heads = [r for r in head_rects if wr.y0-2 <= r.y0 and r.y1 <= wr.y1+2]
        has_header = bool(heads)
        blocks.append({'t': 'table', 'y': wr.y0, 'cols': ncols,
                       'header': rows[0] if has_header else None,
                       'rows': rows[1:] if has_header else rows,
                       'col_x': cols_x})

    # hrs
    for c, r in strokes:
        if r.width > 300 and r.height < 2.5 and 40 < r.y0 < 800:
            if any(wr.x0-2 <= r.x0 and r.x1 <= wr.x1+2 and wr.y0-2 <= r.y0 <= wr.y1+2 for wr in wrappers):
                continue
            blocks.append({'t': 'hr', 'y': r.y0})

    # flow text: keep original lines, merge into paragraphs
    flow = [(bb, sp) for i, (bb, sp) in enumerate(orig_lines) if not used[i]]
    flow.sort(key=lambda t: (round(t[0].y0, 0), t[0].x0))
    cur = None
    for bb, sp in flow:
        runs = [mk_run(s) for s in sorted(sp, key=lambda s: s['bbox'][0])]
        txt = ''.join(r['text'] for r in runs)
        size = max(s['size'] for s in sp)
        clipped = any(s['bbox'][2] > CLIP_X for s in sp)
        is_disc = any(d.y0 - 4 <= (bb.y0+bb.y1)/2 <= d.y1 + 4 for d in discs) or bb.x0 > 58
        if is_disc and cur is not None and cur['t'] == 'bul' and bb.x0 > 58 and not any(d.y0 - 4 <= (bb.y0+bb.y1)/2 <= d.y1 + 4 for d in discs):
            # continuation line of bullet
            if cur['runs'] and runs:
                a = cur['runs'][-1]['text']
                if a and runs[0]['text'] and not a.endswith(' ') and not runs[0]['text'].startswith((' ', '.', ',', ';', ':', ')', ']')):
                    cur['runs'].append({'text': ' ', 'size': 9.8, 'mono': False, 'bold': False, 'italic': False, 'color': '#241c14', 'x1': 0})
            cur['runs'].extend(runs)
            cur['_lasty'] = bb.y0
            cur['clipped'] = cur.get('clipped', False) or clipped
            continue
        if txt.lstrip().startswith(('•', '‧', '·')) or any(d.y0 - 4 <= (bb.y0+bb.y1)/2 <= d.y1 + 4 for d in discs):
            runs[0]['text'] = runs[0]['text'].lstrip()
            while runs and not runs[0]['text']: runs.pop(0)
            if runs: runs[0]['text'] = runs[0]['text'].lstrip('•‧· ')
            blocks.append({'t': 'bul', 'y': bb.y0, 'runs': runs, 'clipped': clipped})
            cur = None
            continue
        if size >= 19:
            blocks.append({'t': 'h1', 'y': bb.y0, 'text': txt, 'size': round(size, 1),
                           'color': runs[0]['color']})
            cur = None
            continue
        if txt.strip() == 'BACK TO CONTENTS':
            blocks.append({'t': 'back', 'y': bb.y0})
            cur = None
            continue
        serif_reg = ''.join(r['text'] for r in runs if not r['bold'] and not r['mono'])
        starts_bold = runs and runs[0]['bold']
        if starts_bold and len(txt) < 80 and len(serif_reg.strip()) < 5:
            blocks.append({'t': 'h2', 'y': bb.y0, 'runs': runs, 'clipped': clipped})
            cur = None
            continue
        if cur is not None and bb.y0 - cur['_lasty'] < 27:
            # join wrapped line
            if cur['runs'] and runs:
                a, b2 = cur['runs'][-1]['text'], runs[0]['text']
                if a and b2 and not a.endswith((' ', '\n')) and not b2.startswith((' ', '.', ',', ';', ':', ')', ']', '’', "'", '"')):
                    cur['runs'].append({'text': ' ', 'size': runs[0]['size'], 'mono': False,
                                        'bold': False, 'italic': False, 'color': runs[0]['color'], 'x1': 0})
            cur['runs'].extend(runs)
            cur['_lasty'] = bb.y0
            cur['clipped'] = cur.get('clipped', False) or clipped
        else:
            cur = {'t': 'p', 'y': bb.y0, 'runs': runs, '_lasty': bb.y0, 'clipped': clipped}
            blocks.append(cur)
    for b in blocks:
        b.pop('_lasty', None)
    blocks.sort(key=lambda b: b['y'])
    model['pages'].append({'pno': pno, 'blocks': blocks})

json.dump(model, open('work/model_raw.json', 'w'), indent=1)
print('pages:', len(model['pages']))
clipped = []
for pg in model['pages']:
    for b in pg['blocks']:
        if b.get('clipped'):
            if b['t'] == 'table':
                for ri, row in enumerate(b['rows']):
                    for ci, c in enumerate(row):
                        if c['clipped']:
                            clipped.append((pg['pno'], 'table', ri, ci, ' | '.join(''.join(r['text'] for r in ln) for ln in c['lines'])))
            elif b['t'] == 'code':
                clipped.append((pg['pno'], 'code', ' | '.join(''.join(r['text'] for r in ln) for ln in b['lines'])))
            else:
                clipped.append((pg['pno'], b['t'], ''.join(r['text'] for r in b['runs'])))
print('CLIPPED ITEMS:', len(clipped))
for c in clipped:
    print(c)
