# MSCI US/Taiwan Index Review Event Dataset

This package contains MSCI public-list parsing code and cleaned outputs for USA / Taiwan additions and deletions from MSCI Standard and Small Cap index review PDFs.

## Key files

- `data/msci_us_taiwan_backtest_ready.xlsx` — Excel workbook with ready events, full audit table, and name → ticker mapping tables.
- `parsed/msci_us_taiwan_events_flat_backtest_ready.csv` — backtest-ready flat event table.
- `parsed/msci_us_taiwan_events_flat_audit_verified.csv` — full event table with mapping/audit gates.
- `parsed/msci_us_taiwan_events_dict_verified.json` — nested JSON version of verified events.
- `parsed/msci_us_taiwan_name_ticker_mapping_verified.csv` — full name → ticker mapping table.
- `research_state/msci_taiwan_mapping_round8e_manual_unique.csv` — final Taiwan manual review list after broad Yahoo/Google/historical lookup; currently empty.
- `research_state/msci_taiwan_mapping_round8*_accepted.csv` — accepted Taiwan mappings from broader web/Yahoo/Google/historical rounds.
- `reports/msci_taiwan_mapping_round8e_completion_report.md` — final Taiwan completion note.
- `scripts/round8*_taiwan_*.py` and `scripts/round5_full_consistency_exports.py` — completion and export workflow.

## Current Taiwan mapping status after Round 8e

- Taiwan unique MSCI names: 754
- With stock code: 754
- Still missing stock code / manual review: 0
- Taiwan event rows: 1,548
- Taiwan event rows with code: 1,548
- Taiwan backtest-ready event rows: 1,423

## Notes

- Source documents are MSCI public-list PDFs. PDFs are not included here to keep the repository lightweight.
- Taiwan mappings include current listed, renamed, merged, delisted, and historical company/security names when source evidence was strong enough.
- `mapping_source` records whether evidence came from local official/reference data, historical sources, Yahoo Finance/Google-searchable pages, MOPS/MoneyDJ/news, or company/market profile pages.
- Some historical Taiwan codes are mapped but not backtest-ready if the ticker is not present in the local reference/price universe used by the audit gate.
- No Google Drive links are required; use GitHub raw files or release ZIP assets.
