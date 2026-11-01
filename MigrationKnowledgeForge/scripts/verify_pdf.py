#!/usr/bin/env python3
"""QA gate for forged cookbook PDFs.

Checks:
 1. no text span crosses the content right edge (clipping regression);
 2. every required string is present (whitespace-insensitive), e.g. completed cells.
Usage:
    python3 verify_pdf.py --pdf book.pdf --max-x 546.5 --must-file must.txt
    python3 verify_pdf.py --pdf book.pdf --must "a string|other string"
Exit 1 on any failure.
"""
import argparse
import re
import sys

import pymupdf


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pdf', required=True)
    ap.add_argument('--max-x', type=float, default=546.5)
    ap.add_argument('--must', default='', help='pipe-separated required strings')
    ap.add_argument('--must-file', help='file with one required string per line')
    args = ap.parse_args()

    doc = pymupdf.open(args.pdf)
    bad = []
    for i, page in enumerate(doc):
        for b in page.get_text('dict')['blocks']:
            if 'lines' not in b:
                continue
            for l in b['lines']:
                for s in l['spans']:
                    if s['bbox'][2] > args.max_x:
                        bad.append((i, round(s['bbox'][2], 1), s['text'][:50]))
    print('overflow spans:', len(bad))
    for x in bad[:10]:
        print('  ', x)

    flat = re.sub(r'\s+', '', '\n'.join(p.get_text() for p in doc))
    required = [s for s in args.must.split('|') if s.strip()]
    if args.must_file:
        required += [l.strip() for l in open(args.must_file) if l.strip()]
    missing = [r for r in required if re.sub(r'\s+', '', r) not in flat]
    print('required strings missing:', len(missing))
    for m in missing[:10]:
        print('  ', m)
    print('pages:', len(doc))
    sys.exit(1 if (bad or missing) else 0)


if __name__ == '__main__':
    main()
