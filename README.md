# Troy SD Check Register Reconciliation · FY11-FY26

Interactive dashboard and master workbook reconciling Troy School District (MI) check-register expenditures from FY2011 (partial) through FY2026-to-date, sourced from BoardDocs Treasurer's Reports and embedded check-register sections in board-meeting packets.

## Deliverables (repo root)

| File | What it is |
|---|---|
| `index.html` | Interactive dashboard (static, all data inlined). Open in any browser. |
| `Troy_SD_Check_Register_FY11-FY26.xlsx` | Master workbook — 8 sheets including both Meeting-FY and Issue-Date-FY pivots. 219,225 line items. |

## Coverage

- **FY11-FY20**: 149,742 line items extracted from embedded check registers in monthly board-meeting packet PDFs (FY11 partial — bundle starts Jan 2011; FY17/FY22/FY23/FY25 fully complete; others have 1-7 month gaps)
- **FY21-FY26**: 69,483 line items from 68 standalone "Check register by fund" PDFs (BoardDocs began separating Aug 2020)
- **Total**: 219,225 line items, $1,195,922,046.69 across 16 fiscal years
- **Two FY columns** in the workbook: `Fiscal Year` (FY of the approving meeting, legacy) and `Issue Date FY` (true transaction FY, recommended for analysis)

## Project layout

```
tsd-checkregister/                           ← repo root (deliverables only)
├── index.html                               ← dashboard (static, hand-edited, data inlined)
├── Troy_SD_Check_Register_FY11-FY26.xlsx    ← master workbook
├── README.md                                ← this file
├── PROMPTS.md                               ← structured build-prompt scaffold
└── Working Folder/                          ← tooling, source data, prompt history
    ├── Prompts/                             ← per-prompt archive + running.md log
    └── Cache and Tools/
        ├── build/                           ← parser, categorizer, rebuild scripts (Python)
        ├── source_data/
        │   └── BoardDocs_PDFs/              ← 68 standalone monthly check-register PDFs (FY20 tail → Feb 2026)
        └── project_docs/
            └── INDEX.md                     ← provenance, FY coverage, known gaps
```

All source PDFs are now bundled inside the project under `source_data/`:
- `BoardDocs_PDFs/` — 68 standalone monthly registers (FY20-tail through Feb 2026)
- `BoardDocs_PDFs_pre2020/` — 83 board-meeting packets containing embedded registers (FY12-FY19)

## Reproducibility

The original FY23-FY26 dashboard and workbook were built via the Claude.ai web interface; those prompts were not captured. The FY21-FY22 backfill (April 2026) and FY12-FY19 backfill (May 2026) were performed via Claude Code with full source under `Working Folder/Cache and Tools/build/`:

- `parser.py` — Pentamation check register PDF parser (regex-based, validated to within 0 rows / $0.00 against original FY23-FY26 totals: 47,917 rows / $417,275,260.96)
- `pre2020_extract.py` — embedded-register extractor for 2011-2019 board-meeting packets; handles em-dash normalization
- `categorize_v2.py` — line categorization (vendor lookup + Michigan PSAM function-code rules)
- `full_parse.py` — orchestrator: parses all PDFs, applies categorization, emits `all_lines.pkl`
- `build_combined_wb.py` — combines pre-2020 + post-2020, applies categorization + subject classification, builds the 7-sheet xlsx
- `rebuild_dashboard.py` — rebuilds the inlined JSON payload in `index.html`

To re-run end-to-end:
```bash
cd "Working Folder/Cache and Tools/build"
python full_parse.py            # parse 68 standalone PDFs → all_lines.pkl  (~7 min)
python pre2020_extract.py       # extract 84 embedded registers → pre2020_lines.pkl  (~30 min)
python build_combined_wb.py     # merge + classify + build xlsx
python rebuild_dashboard.py     # update index.html payload
```

See [`PROMPTS.md`](PROMPTS.md) for the prompt scaffold and [`Working Folder/Prompts/running.md`](Working%20Folder/Prompts/running.md) for the chronological prompt log.

## Source

All check registers were pulled from BoardDocs (https://go.boarddocs.com/mi/troysd/Board.nsf/Public). For FY21+, each was attached to the Treasurer's Report agenda item of the corresponding Regular Board of Education meeting. For FY12-FY19, the registers are embedded inside the larger meeting-packet PDFs (typically pages 30+ of a 100-250 page packet). Filenames are prefixed with the meeting date (`YYYY-MM-DD`) for sortability; the period each register actually covers is stated inside the PDF (typically meeting date minus ~2 months).

See `Working Folder/Cache and Tools/project_docs/INDEX.md` for fiscal-year coverage and known gaps.

## License

MIT — see [`LICENSE`](LICENSE).
