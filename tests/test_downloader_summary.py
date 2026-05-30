from bajador_yt.downloader import summarize
from bajador_yt.models import DownloadResult


def test_summarize_counts_all_statuses() -> None:
    results = [
        DownloadResult(url='a', status='success', message=''),
        DownloadResult(url='b', status='success', message=''),
        DownloadResult(url='c', status='skipped', message=''),
        DownloadResult(url='d', status='invalid', message=''),
        DownloadResult(url='e', status='error', message=''),
        DownloadResult(url='f', status='cancelled', message=''),
    ]
    assert summarize(results) == {
        'success': 2,
        'skipped': 1,
        'invalid': 1,
        'error': 1,
        'cancelled': 1,
    }


def test_summarize_empty() -> None:
    assert summarize([]) == {
        'success': 0,
        'skipped': 0,
        'invalid': 0,
        'error': 0,
        'cancelled': 0,
    }
