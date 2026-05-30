import pytest

from bajador_yt.validators import (
    is_supported_audio_format,
    is_supported_mode,
    is_supported_quality,
    is_supported_video_format,
    is_valid_youtube_url,
)


@pytest.mark.parametrize(
    'url',
    [
        'https://www.youtube.com/watch?v=abc123',
        'https://youtube.com/watch?v=abc123',
        'http://youtube.com/watch?v=abc',
        'https://m.youtube.com/watch?v=abc',
        'https://music.youtube.com/watch?v=abc',
        'https://youtu.be/abc123',
    ],
)
def test_valid_urls(url: str) -> None:
    assert is_valid_youtube_url(url)


@pytest.mark.parametrize(
    'url',
    [
        '',
        None,
        'ftp://youtube.com/abc',
        'https://vimeo.com/123',
        'notaurl',
        'https://evil.com/youtube.com',
        'https://youtube.com.evil.com/watch',
    ],
)
def test_invalid_urls(url) -> None:
    assert not is_valid_youtube_url(url or '')


def test_supported_sets() -> None:
    assert is_supported_mode('audio')
    assert is_supported_mode('video')
    assert not is_supported_mode('other')

    assert is_supported_audio_format('mp3')
    assert not is_supported_audio_format('flac')

    assert is_supported_video_format('mp4')
    assert not is_supported_video_format('avi')

    assert is_supported_quality('192')
    assert not is_supported_quality('999')
