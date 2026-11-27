"""The document registry: data/registry.csv, one row per annual report.

The registry is the single source of truth for which company and financial
year a document belongs to. Metadata and filters read it from here; nothing
guesses a company or a year from the PDF's text.

Columns (in this order):

    doc_id        infosys_ar_fy2025      lowercase letters, digits, underscores
    company       infosys                company id, same rules
    company_name  Infosys Limited
    aliases       Infosys|Infosys Ltd    names a question might use, "|"-separated
    fy            FY2025                 April 2024 to March 2025
    url           https://...            where the PDF was downloaded from
    pages         412                    page count (0 until downloaded)
    sha256        9f2c...                checksum of the PDF ("" until downloaded)

The PDF for a row lives at <corpus.pdf_dir>/<doc_id>.pdf (see `pdf_path`).
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from rag.schema import RegistryEntry

COLUMNS = ["doc_id", "company", "company_name", "aliases", "fy", "url", "pages", "sha256"]

_ID = re.compile(r"[a-z0-9_]+")
_FY = re.compile(r"FY\d{4}")
_SHA = re.compile(r"[0-9a-f]{64}")


class RegistryError(ValueError):
    """registry.csv is wrong. The message names the file and the line."""


def load_registry(path: str | Path) -> dict[str, RegistryEntry]:
    """Read registry.csv into {doc_id: RegistryEntry}, checking every row."""
    path = Path(path)
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLUMNS:
            raise RegistryError(
                f"{path}: header must be exactly {','.join(COLUMNS)}, got {reader.fieldnames}"
            )
        entries: dict[str, RegistryEntry] = {}
        for row in reader:
            where = f"{path}:{reader.line_num}"
            entry = _parse_row(row, where)
            if entry.doc_id in entries:
                raise RegistryError(f"{where}: duplicate doc_id '{entry.doc_id}'")
            entries[entry.doc_id] = entry
    return entries


def _parse_row(row: dict[str, str], where: str) -> RegistryEntry:
    values = {key: (row.get(key) or "").strip() for key in COLUMNS}

    for key in ("doc_id", "company"):
        if not _ID.fullmatch(values[key]):
            raise RegistryError(f"{where}: {key} '{values[key]}' must use only a-z, 0-9 and '_'")
    if not values["company_name"]:
        raise RegistryError(f"{where}: company_name is empty")
    if not _FY.fullmatch(values["fy"]):
        raise RegistryError(f"{where}: fy '{values['fy']}' must look like FY2025")
    if values["sha256"] and not _SHA.fullmatch(values["sha256"]):
        raise RegistryError(f"{where}: sha256 must be 64 lowercase hex characters, or empty")
    try:
        pages = int(values["pages"] or 0)
    except ValueError:
        raise RegistryError(f"{where}: pages '{values['pages']}' is not a whole number") from None
    if pages < 0:
        raise RegistryError(f"{where}: pages cannot be negative")

    aliases = [a.strip() for a in values["aliases"].split("|") if a.strip()]
    if values["company_name"] not in aliases:
        aliases.insert(0, values["company_name"])  # the full name always counts

    return RegistryEntry(
        doc_id=values["doc_id"],
        company=values["company"],
        company_name=values["company_name"],
        aliases=aliases,
        fy=values["fy"],
        url=values["url"],
        pages=pages,
        sha256=values["sha256"],
    )


def pdf_path(entry: RegistryEntry, pdf_dir: str | Path) -> Path:
    """Where this document's PDF is expected on disk."""
    return Path(pdf_dir) / f"{entry.doc_id}.pdf"
