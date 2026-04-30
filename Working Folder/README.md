# Working Folder

Source data and project documentation for the Check Register Reconciliation project. The user-facing artifacts (`index.html`, `Troy_SD_Check_Register_FY23-FY26.xlsx`) live at the **repo root**, not here.

## Layout

```
tsd-checkregister/                           (git repo root — single source of truth for deliverables)
├── index.html                               ← dashboard (static, hand-edited)
├── Troy_SD_Check_Register_FY23-FY26.xlsx    ← master workbook
├── README.md
├── PROMPTS.md                               ← structured build-prompt scaffold (reproducibility)
└── Working Folder/                          ← THIS FOLDER
    ├── README.md                            ← this file
    ├── Prompts/
    │   ├── running.md                       ← chronological one-line prompt log
    │   ├── TEMPLATE/                        ← shape of each timestamped prompt entry
    │   └── <YYYY-MM-DD_HH-MM-SS>/           ← one folder per logged prompt
    └── Cache and Tools/
        ├── source_data/
        │   └── BoardDocs_PDFs/              ← 45 monthly check-register PDFs from BoardDocs
        └── project_docs/
            └── INDEX.md                     ← source notes, FY coverage, known gaps
```

## Status

The dashboard and xlsx were built through the Claude.ai web interface during the initial pull from BoardDocs. They are kept here as static artifacts; there is no automated rebuild pipeline yet, and the original prompts were not captured at the time.

A scaffold for prompt history now exists under `Prompts/` and at the root in [`PROMPTS.md`](../PROMPTS.md). The intent is that any future revision (refresh of FY data, dashboard changes, extraction pipeline work) is performed through Claude Code with prompts logged in both places, so the project remains reproducible end-to-end going forward. If the original Claude.ai conversations are recovered, they can be backfilled into the same structure.

If/when an extraction pipeline is added, it will follow the same pattern as the sibling `tsd-achievement` repo: scripts in `Cache and Tools/`, intermediate CSVs in `Cache and Tools/extracted_data/`, a portable `_paths.py`, and a `rebuild.command` that writes the xlsx directly to the repo root.
