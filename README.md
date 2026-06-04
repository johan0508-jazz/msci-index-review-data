# MSCI US/Taiwan Index Review Event Dataset

This package contains MSCI public-list parsing code and cleaned outputs for USA / Taiwan additions and deletions from MSCI Standard and Small Cap index review PDFs.

## Key files

- `data/msci_us_taiwan_backtest_ready.xlsx` — Excel workbook with ready events, mapping tables, Taiwan manual review rows, and metadata.
- `parsed/msci_us_taiwan_events_flat_backtest_ready.csv` — backtest-ready flat event table.
- `parsed/msci_us_taiwan_events_flat_audit_verified.csv` — full event table with mapping/audit gates.
- `parsed/msci_us_taiwan_name_ticker_mapping_verified.csv` — full name → ticker mapping table.
- `research_state/msci_taiwan_mapping_round7_manual_unique.csv` — Taiwan names still missing code after conservative completion; intended for human review.
- `research_state/msci_taiwan_mapping_round7_accepted.csv` and `round7b_accepted.csv` — newly accepted Taiwan mappings.
- `scripts/round7_taiwan_mapping_completion.py` and `scripts/round7b_taiwan_variant_completion.py` — Taiwan mapping completion workflow.

## Current Taiwan mapping status after Round 7/7b

- Taiwan unique MSCI names: 754
- With stock code: 665
- Still missing stock code / manual review: 89
- Taiwan event rows: 1,548
- Taiwan backtest-ready event rows: 1,323

## Notes

- Source documents are MSCI public-list PDFs. PDFs are not included here to keep the repository lightweight.
- Current Taiwan rows use official/local TWSE/TPEx/FinLab reference-universe confirmation; Yahoo Finance search is used only as a name-discovery aid when the code exists in the local official/current universe.
- Historical delisted rows are accepted only from official TWSE/TPEx delisted sources or prior manually reviewed evidence. Some historical codes remain not backtest-ready if not present in the local price/reference universe.
- The remaining manual list should be verified against MOPS/TWSE/TPEx/company IR before writing codes back.
