# Pipeline A — repair a clipped PDF book & rebuild it

Symptom: book printed by a headless browser; tables/code sit in `overflow-x`
containers; right side hard-clipped at a container edge (often a scrollbar is
printed under tables). Clipped glyphs are absent from the content stream —
they must be **completed**, not copied.

## 1. Extract the document model

```bash
python3 scripts/pdf_extract.py --pdf broken.pdf --out model.json --clip-x 545.3
```

- Geometry-driven: fill colours classify code blocks / table wrappers / headers /
  row stripes / borders / bullet discs; spans are assigned to cells by column &
  row boundaries; paragraphs re-joined by line-gap threshold (~27pt at 12.8pt body).
- `--clip-x`: spans ending beyond it are flagged `clipped` (per cell / code line).
- Fonts: `--styles map.json` overrides mono/bold/italic inference (Type3 subsets
  carry no names; inference uses flags + width ratio).
- Tables split across pages merge automatically when headers repeat.

## 2. Complete the clipped content (provenance tiers)

1. same value elsewhere in the corpus (other page, appendix, flattened md);
2. public source tree of the target version (fetch raw file, grep, quote path);
3. reconstruction — flag it in the changelog; vendor-private values get **[EE-verify]**.

Apply completions as asserted ops on `model.json` (assert the visible fragment
before replacing, so a shifted table fails loudly — see Vol-I `patch_model.py` pattern).

## 3. Re-render

```python
from booklib import Book, T, C
b = Book('Title')          # cover/toc/chapter/p/bul/code/table emitters
b.write_html('book.html'); b.write_pdf('book.html', 'book.pdf')
```

House CSS already wraps chips and code (`overflow-wrap: anywhere`), fixes tables
to page width (`table-layout: fixed` + colgroup %) — clipping cannot recur.
Sanitize pass (branding/PII removal) runs over the model *before* rendering.

## 4. Verify

```bash
python3 scripts/verify_pdf.py --pdf book.pdf --max-x 546.5 --must-file completed.txt
```

0 overflow spans + all completed strings present (whitespace-insensitive).
Spot-render 3–5 formerly clipped pages to PNG and eyeball them.
