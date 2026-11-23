"""F-04: registry loading and validation."""

from pathlib import Path

import pytest

from rag.registry import COLUMNS, RegistryError, load_registry, pdf_path

FIXTURES = Path(__file__).parent / "fixtures"
HEADER = ",".join(COLUMNS)
GOOD = "acme_ar_fy2025,acme,Acme Industries Limited,Acme|Acme Ltd,FY2025,https://x,6,"


def write(tmp_path: Path, *rows: str, header: str = HEADER) -> Path:
    path = tmp_path / "registry.csv"
    path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")
    return path


def test_fixture_registry_loads_and_points_at_the_pdf():
    reg = load_registry(FIXTURES / "registry.csv")
    entry = reg["acme_ar_fy2025"]
    assert entry.fy == "FY2025" and entry.pages == 6
    assert pdf_path(entry, FIXTURES).exists()


def test_full_name_is_always_an_alias(tmp_path):
    entry = load_registry(write(tmp_path, GOOD))["acme_ar_fy2025"]
    assert entry.aliases == ["Acme Industries Limited", "Acme", "Acme Ltd"]


def test_empty_pages_and_sha_are_allowed_before_download(tmp_path):
    entry = load_registry(write(tmp_path, GOOD.replace(",6,", ",,")))["acme_ar_fy2025"]
    assert entry.pages == 0 and entry.sha256 == ""


@pytest.mark.parametrize(
    ("row", "fragment"),
    [
        (GOOD.replace("FY2025", "2024-25"), "FY2025"),
        (GOOD.replace("acme_ar_fy2025", "Acme AR"), "doc_id"),
        (GOOD.replace(",acme,", ",ACME,"), "company"),
        (GOOD.replace(",6,", ",six,"), "pages"),
        (GOOD + "abc", "sha256"),
        (GOOD.replace("Acme Industries Limited", ""), "company_name"),
    ],
)
def test_bad_rows_raise_with_line_number(tmp_path, row, fragment):
    with pytest.raises(RegistryError, match=fragment) as err:
        load_registry(write(tmp_path, row))
    assert "registry.csv:2" in str(err.value)


def test_duplicate_doc_id(tmp_path):
    with pytest.raises(RegistryError, match="duplicate"):
        load_registry(write(tmp_path, GOOD, GOOD))


def test_wrong_header(tmp_path):
    with pytest.raises(RegistryError, match="header"):
        load_registry(write(tmp_path, GOOD, header="id,company"))
