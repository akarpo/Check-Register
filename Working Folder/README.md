# Working Folder

Source data and project documentation for the Check Register Reconciliation project. The user-facing artifacts (`index.html`, `Troy_SD_Check_Register_FY23-FY26.xlsx`) live at the **repo root**, not here.

## Layout

```
Check-Register/                              (git repo root — single source of truth for deliverables)
├── index.html                               ← dashboard (static, hand-edited)
├── Troy_SD_Check_Register_FY23-FY26.xlsx    ← master workbook
├── README.md
└── Working Folder/                          ← THIS FOLDER
    ├── README.md                            ← this file
    └── Cache and Tools/
        ├── source_data/
        │   └── BoardDocs_PDFs/              ← 45 monthly check-register PDFs from BoardDocs
        └── project_docs/
            └── INDEX.md                     ← source notes, FY coverage, known gaps
```

## Status

The dashboard and xlsx were built through the Claude.ai web interface during the initial pull from BoardDocs. They are kept here as static artifacts; there is no automated rebuild pipeline yet.

If/when an extraction pipeline is added, it will follow the same pattern as the sibling `Achievement` repo: scripts in `Cache and Tools/`, intermediate CSVs in `Cache and Tools/extracted_data/`, a portable `_paths.py`, and a `rebuild.command` that writes the xlsx directly to the repo root.
