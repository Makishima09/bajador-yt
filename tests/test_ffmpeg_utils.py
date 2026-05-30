from pathlib import Path

from bajador_yt import ffmpeg_utils
from bajador_yt.ffmpeg_utils import detect_ffmpeg_path, validate_ffmpeg_path


def test_validate_ffmpeg_path_none() -> None:
    assert validate_ffmpeg_path(None) is None
    assert validate_ffmpeg_path('') is None


def test_validate_ffmpeg_path_missing(tmp_path) -> None:
    assert validate_ffmpeg_path(str(tmp_path / 'no-existe')) is None


def test_validate_ffmpeg_path_present(tmp_path) -> None:
    fake = tmp_path / 'ffmpeg'
    fake.write_text('')
    assert validate_ffmpeg_path(str(fake)) == str(fake)


def test_detect_ffmpeg_prefers_env(monkeypatch, tmp_path) -> None:
    fake = tmp_path / 'ffmpeg'
    fake.write_text('')
    monkeypatch.setenv('FFMPEG_PATH', str(fake))
    monkeypatch.setattr(ffmpeg_utils.shutil, 'which', lambda _: None)
    assert detect_ffmpeg_path() == str(fake)


def test_detect_ffmpeg_uses_which(monkeypatch) -> None:
    monkeypatch.delenv('FFMPEG_PATH', raising=False)
    monkeypatch.setattr(ffmpeg_utils.shutil, 'which', lambda _: '/usr/local/bin/ffmpeg')
    monkeypatch.setattr(ffmpeg_utils.os.path, 'exists', lambda _: False)
    assert detect_ffmpeg_path() == '/usr/local/bin/ffmpeg'


def test_detect_ffmpeg_returns_none_when_nothing(monkeypatch) -> None:
    monkeypatch.delenv('FFMPEG_PATH', raising=False)
    monkeypatch.setattr(ffmpeg_utils.shutil, 'which', lambda _: None)
    monkeypatch.setattr(ffmpeg_utils.os.path, 'exists', lambda _: False)
    assert detect_ffmpeg_path() is None
