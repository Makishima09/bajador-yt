import pytest

from bajador_yt.csv_utils import CsvFormatError, extract_links_from_csv, extract_links_from_text


def test_extract_links_from_text_basic() -> None:
    assert extract_links_from_text('a\nb\n  c  \n\n') == ['a', 'b', 'c']


def test_extract_links_from_text_empty() -> None:
    assert extract_links_from_text('') == []
    assert extract_links_from_text('   \n\n') == []


def test_extract_links_from_csv_ok(tmp_path) -> None:
    csv_file = tmp_path / 'urls.csv'
    csv_file.write_text(
        'link\nhttps://youtu.be/abc\nhttps://youtu.be/def\n',
        encoding='utf-8',
    )
    assert extract_links_from_csv(csv_file) == ['https://youtu.be/abc', 'https://youtu.be/def']


def test_extract_links_from_csv_missing_column(tmp_path) -> None:
    csv_file = tmp_path / 'bad.csv'
    csv_file.write_text('url\nhttps://youtu.be/abc\n', encoding='utf-8')
    with pytest.raises(CsvFormatError):
        extract_links_from_csv(csv_file)


def test_extract_links_from_csv_empty_rows_ignored(tmp_path) -> None:
    csv_file = tmp_path / 'urls.csv'
    csv_file.write_text('link\n\nhttps://youtu.be/abc\n   \n', encoding='utf-8')
    assert extract_links_from_csv(csv_file) == ['https://youtu.be/abc']
