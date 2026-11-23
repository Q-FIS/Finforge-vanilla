# [EVAL-01] Download the 6 annual reports and fill in the registry
labels: team:eval, size:S
**Owner:** E1 · **Size:** S (1 day) · **Due:** day 3 · **Needs:** nothing, start now

## What is this, in plain words?
Our whole project runs on 6 real documents: the FY2024 and FY2025 annual
reports of **Infosys**, **Asian Paints** and **Titan Company**. You get them,
check they're usable, and list them in `data/registry.csv`, the one file that
says which document is which company and year. Everything else (metadata,
filters, questions) reads company and year from there, never guesses them.

## Step by step
1. **Download** each report as a PDF from the company's investor-relations website (search "<company> annual report 2024-25"). FY2025 = the report for April 2024 to March 2025.
2. **Name** each file `data/pdfs/<doc_id>.pdf`, using these ids:
   `infosys_ar_fy2024`, `infosys_ar_fy2025`, `asianpaints_ar_fy2024`, `asianpaints_ar_fy2025`, `titan_ar_fy2024`, `titan_ar_fy2025`.
3. **Check each one has real text:** open it, and try to select and copy a paragraph. If you can't, it's a scanned image: swap that company for Larsen & Toubro or Dr. Reddy's, and tell the lead.
4. **Fill `data/registry.csv`**, one row per report (the first line, the header, is already there):
   ```
   doc_id,company,company_name,aliases,fy,url,pages,sha256
   infosys_ar_fy2025,infosys,Infosys Limited,Infosys|Infosys Ltd|Infosys Limited|INFY,FY2025,https://...,312,9f2c...
   ```
   - `company`: lowercase, no spaces (`asianpaints`).
   - `aliases`: every name a question might use, separated by `|`. Think about how people write it: "Asian Paints", "Asian Paints Ltd", "APL"...
   - `pages`: the page count, from your PDF viewer.
   - `sha256`: run `sha256sum data/pdfs/*.pdf` and copy each long code. It proves everyone has the exact same file.
5. **Check it loads:**
   `uv run python -c "from rag.registry import load_registry; print(load_registry('data/registry.csv'))"`
6. **Share the PDFs** in the club drive, because PDFs never go in git (they're big). Add one line to `README.md` saying where they are.

## Done when
- [ ] 6 rows in `data/registry.csv` that load without errors
- [ ] The 6 PDFs are in the club drive, and `README.md` says where
- [ ] Everyone can download them into `data/pdfs/`, and the sha256 values match
