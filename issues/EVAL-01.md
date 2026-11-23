# [EVAL-01] Download the 6 annual reports and fill the registry
labels: team:eval, size:S
**Owner:** E1 · **Size:** S (1 day) · **Due:** day 3 · **Needs:** nothing, start now

## In one sentence
Get the FY2024 and FY2025 annual reports of Infosys, Asian Paints and Titan Company, and list them in `data/registry.csv`.

## What to do
1. Download each report from the company's investor-relations website (DECISIONS.md D4 says why these three).
2. Save each as `data/pdfs/<doc_id>.pdf`, for example `data/pdfs/infosys_ar_fy2025.pdf`. **PDFs are never committed to git**; share them in the club drive.
3. Quick check: open each one and try to select and copy text. If you can't, it's a scanned report: swap that company for Larsen & Toubro or Dr. Reddy's, and tell the lead.
4. Fill `data/registry.csv`, one row per report:
   `doc_id, company, company_name, aliases, fy, url, pages, sha256`
   - aliases: names a question might use, separated by `|`, e.g. `Infosys|Infosys Ltd|Infosys Limited`
   - sha256: run `sha256sum data/pdfs/*.pdf`
5. Check it loads: `uv run python -c "from rag.registry import load_registry; print(load_registry('data/registry.csv'))"`

## Done when
- [ ] 6 rows in `data/registry.csv` that load without errors
- [ ] The 6 PDFs are in the club drive, and the README says where
