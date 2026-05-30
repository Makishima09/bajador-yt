import pytest

from bajador_yt.errors import classify_error, is_retryable, user_friendly_message


@pytest.mark.parametrize(
    'message, expected',
    [
        ('This video is private', 'private'),
        ('Video unavailable: has been removed by the uploader', 'unavailable'),
        ('not available in your country', 'geo_blocked'),
        ('HTTP Error 403: Forbidden', 'forbidden'),
        ('copyright claim', 'copyright'),
        ('Sign in to confirm your age', 'age_restricted'),
        ('ERROR: [youtube] abc: Please sign in', 'login_required'),
        ('Login required to view this content', 'login_required'),
        ('Connection timed out', 'timeout'),
        ('No supported JavaScript runtime', 'js_runtime'),
        ('Temporary failure in name resolution', 'network'),
        ('Unable to extract video data', 'extractor'),
        ('Postprocessing: WARNING: unable to obtain file audio codec with ffprobe', 'postprocessing'),
        ('ffmpeg not found', 'postprocessing'),
        ('Something else', 'generic'),
    ],
)
def test_classify_error(message: str, expected: str) -> None:
    assert classify_error(Exception(message)) == expected


def test_classify_none() -> None:
    assert classify_error(None) == 'generic'


def test_is_retryable_network_yes() -> None:
    assert is_retryable('network')
    assert is_retryable('timeout')
    assert is_retryable('forbidden')


def test_is_retryable_private_no() -> None:
    assert not is_retryable('private')
    assert not is_retryable('unavailable')
    assert not is_retryable('geo_blocked')
    assert not is_retryable('login_required')
    assert not is_retryable('age_restricted')


def test_user_friendly_message_contains_detail() -> None:
    exc = Exception('boom')
    msg = user_friendly_message(exc, 'network')
    assert 'red' in msg.lower()
    assert 'boom' in msg
