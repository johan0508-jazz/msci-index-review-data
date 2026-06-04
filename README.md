# MSCI US/Taiwan Index Review Event Dataset

This package contains the MSCI public-list parsing code and cleaned outputs for USA / Taiwan additions and deletions from MSCI Standard and Small Cap index review PDFs.

## Key files

- `data/msci_us_taiwan_backtest_ready.xlsx` — Excel workbook with the main event table, verified ticker mapping, and PDF metadata.
- `parsed/msci_us_taiwan_events_flat_backtest_ready.csv` — backtest-ready flat event table.
- `parsed/msci_us_taiwan_name_ticker_mapping_verified_backtest_ready.csv` — verified name → ticker mapping table.
- `parsed/msci_pdf_review_metadata.csv` — review date / source PDF metadata.
- `parsed/msci_us_taiwan_events_dict_verified.json` — nested dict-style export.
- `scripts/parse_msci_us_taiwan_reviews.py` — main parser.
- `scripts/verify_msci_name_ticker_mapping.py` and audit scripts — ticker mapping verification workflow.
- `reports/` — parser and ticker audit notes.

## Notes

- Source documents are MSCI public-list PDFs. The PDFs themselves are not included here to keep the repository lightweight.
- Ticker mapping is research-grade and includes verification/status columns; still re-check critical rows before live trading.
- Dates are separated into issue date, announcement date, and effective close date to avoid look-ahead bias in backtests.
