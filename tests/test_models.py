import pytest

from bajador_yt.models import DownloadResult


def test_download_result_defaults() -> None:
    r = DownloadResult(url='x', status='success', message='ok')
    assert r.output_path is None
    assert r.category is None


def test_download_result_is_frozen() -> None:
    r = DownloadResult(url='x', status='success', message='ok')
    with pytest.raises(Exception):
        r.url = 'y'  # type: ignore[misc]
