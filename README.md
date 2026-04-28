# Troy SD Check Register Reconciliation · FY23-FY26

Interactive dashboard and master workbook reconciling Troy School District (MI) check-register expenditures from FY2023 through FY2026-to-date, sourced from BoardDocs Treasurer's Reports.

## Deliverables (repo root)

| File | What it is |
|---|---|
| `index.html` | Interactive dashboard (static, all data inlined). Open in any browser. |
| `Troy_SD_Check_Register_FY23-FY26.xlsx` | Master workbook — 7 sheets: README, All Lines (47,918 rows), By Year × Fund, By Budget Unit, PD_Yearly_Summary, Curriculum_PD, PD by Subject. |

## Project layout

```
Check-Register/                              ← repo root (deliverables only)
├── index.html                               ← dashboard (static, hand-edited, data inlined)
├── Troy_SD_Check_Register_FY23-FY26.xlsx    ← master workbook
├── README.md                                ← this file
└── Working Folder/                          ← tooling, source data, intermediate work
    └── Cache and Tools/
        ├── source_data/
        │   └── BoardDocs_PDFs/              ← 45 monthly check-register PDFs (FY22 tail → Feb 2026)
        └── project_docs/
            └── INDEX.md                     ← provenance, FY coverage, known gaps
```

The repo root is the single source of truth for deliverables. Everything else lives under `Working Folder/`.

## Source

All check registers were pulled from BoardDocs (https://go.boarddocs.com/mi/troysd/Board.nsf/Public), each attached to the Treasurer's Report agenda item of the corresponding Regular Board of Education meeting. Filenames are prefixed with the meeting date (`YYYY-MM-DD`) for sortability; the period each register actually covers is stated inside the PDF (typically meeting date minus ~2 months).

See `Working Folder/Cache and Tools/project_docs/INDEX.md` for fiscal-year coverage and known gaps.
