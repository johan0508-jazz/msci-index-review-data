# MSCI index review PDF archive
Generated/updated: 2026-05-21 Asia/Taipei
## Local archive
Path: `~/Documents/invest/msci_index_reviews/`
PDF folders:
- `china_all_shares_small`: 40 PDFs
- `smallcap`: 79 PDFs
- `stdindex`: 82 PDFs

Total downloaded PDFs: **201**
Readability check: **201/201 readable**; no unreadable PDFs found.

## URL/name findings
- Standard index review PDFs use `MSCI_{Mon}{YY}_STPublicList.pdf` under `gimi/stdindex/`, e.g. `MSCI_May26_STPublicList.pdf`.
- Small Cap review PDFs use `MSCI_{Mon}{YY}_SCPublicList.pdf` under `gimi/smallcap/` (not `STPublicList`), e.g. `MSCI_May26_SCPublicList.pdf`.
- Valid files found are quarterly review months (`Feb`, `May`, `Aug`, `Nov`). Monthly probes were attempted; non-quarterly months did not resolve for the main Standard/Small Cap families.
- Initial historical sweep attempted 1998-2026; actual public files found start from mid-2000s for the main families.

## Other MSCI similar public-list families found
Search/probing found these additional MSCI public-list patterns:
- China All Shares: `gimi/stdindex/MSCI_{Mon}{YY}_ChinaAllShares_PublicList.pdf`
- China All Shares Small Cap: `gimi/smallcap/MSCI_{Mon}{YY}_SC_ChinaAllShares_PublicList.pdf`
- China A Index Series: `gimi/stdindex/MSCI_{Mon}{YY}_ChinaAPublicList_EN.pdf`
- China A International: `gimi/stdindex/MSCI_{Mon}{YY}_ChinaAIntl_PublicList.pdf`
- Global Micro Cap: `gimi/stdindex/MSCI_{Mon}{YY}_MicroPublicList.pdf`
- Overseas China: `gimi/stdindex/MSCI_{Mon}{YY}_OVCPublicList.pdf`
- Frontier Markets: likely `gimi/stdindex/MSCI_{Mon}{YY}_FM_PublicList.pdf`

Downloaded among these: `china_all_shares_small` 40 PDFs. A later broad supplement probe hit MSCI/Akamai 403 rate/security blocking for the not-yet-downloaded additional families; see `manifest/supplement_manifest.json`. Main requested Standard/Small Cap PDFs were already downloaded before the block.

## FTSE Taiwan findings
- FTSE Russell/LSEG publishes FTSE TWSE Taiwan Index review notices. Examples found: March 2025 annual review notice `https://research.ftserussell.com/products/index-notices/home/getnotice/?id=2615254`; Dec 2023 quarterly review notice `https://research.ftserussell.com/products/index-notices/home/getnotice/?id=2610957`.
- Those notices reference XLSX attachments such as `FTSE_TWSE_Taiwan_Index_Review_TN_March_2025.xlsx`, `FTSE_TWSE_Taiwan_Index_Review_TN_Dec2023.xlsx`, `FTSE_TWSE_Taiwan_Index_Review_TN_Dec2022.xlsx`, and historical `FTSE_TWSE_Taiwan_Index_Review_TN_Jun18_published.xlsx`.
- LSEG FTSE TWSE Taiwan product page confirms the family: Taiwan 50, Taiwan 50 30% Capped, Mid-Cap 100, Technology, Eight Industries, Dividend+, RAFI Taiwan, Shariah.
- Ground rules state reviews are quarterly in March/June/September/December; annual review is March; changes are implemented after close on third Friday/effective Monday.
- Taiwan Index Plus technical-notice pages also expose current/historical review notices and downloadable files, with year filter back to 2002 in search results: `https://taiwanindex.com.tw/en/downloads/technical_notice`.

## Manifests
- `manifest/download_manifest.json`: initial MSCI sweep with URL status and readability fields.
- `manifest/supplement_manifest.json`: all-month supplement probe and additional-family checks.
- `manifest/readability_check.json`: final local PDF readability check using PDF header, macOS metadata page count, `file`, and `strings`.

## Current product coverage summary
- `china_all_shares_small`: 40 PDFs, 2016-2026
- `smallcap`: 79 PDFs, 2006-2026
- `stdindex`: 82 PDFs, 2006-2026

## Additional MSCI products targeted but not yet downloaded
Known public-list product patterns were confirmed by web search, but direct app2.msci.com requests are currently returning Akamai HTTP 403 from this machine after the broad probe. Targeted check saved in `manifest/targeted_other_products_check.json`. Candidate families: `china_all_shares_std`, `china_a`, `china_a_intl`, `micro`, `overseas_china`, `frontier_markets`.
