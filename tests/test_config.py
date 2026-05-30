import json

import pytest

from bajador_yt.config import ConfigError, DownloadConfig, load_config


def test_default_valid() -> None:
    DownloadConfig().validate()


def test_merged_ignores_none_and_unknown() -> None:
    cfg = DownloadConfig().merged({'mode': None, 'unknown': 'x', 'audio_quality': '320'})
    assert cfg.audio_quality == '320'
    assert cfg.mode == 'audio'


def test_validate_bad_mode() -> None:
    with pytest.raises(ConfigError):
        DownloadConfig(mode='invalid').validate()


def test_validate_bad_quality() -> None:
    with pytest.raises(ConfigError):
        DownloadConfig(audio_quality='999').validate()


def test_validate_bad_retries() -> None:
    with pytest.raises(ConfigError):
        DownloadConfig(max_retries=0).validate()


def test_validate_cookies_browser() -> None:
    DownloadConfig(cookies_from_browser='chrome').validate()
    DownloadConfig(cookies_from_browser=None).validate()
    with pytest.raises(ConfigError):
        DownloadConfig(cookies_from_browser='netscape').validate()


def test_load_config_ok(tmp_path) -> None:
    path = tmp_path / 'config.json'
    path.write_text(
        json.dumps(
            {
                'output_folder': './out',
                'audio_quality': '320',
                'parallel_downloads': 2,
                'unknown_field': 'ignored',
            }
        ),
        encoding='utf-8',
    )
    cfg = load_config(path)
    assert cfg.output_folder == './out'
    assert cfg.audio_quality == '320'
    assert cfg.parallel_downloads == 2


def test_load_config_missing(tmp_path) -> None:
    with pytest.raises(ConfigError):
        load_config(tmp_path / 'nope.json')


def test_load_config_bad_json(tmp_path) -> None:
    path = tmp_path / 'bad.json'
    path.write_text('{ broken', encoding='utf-8')
    with pytest.raises(ConfigError):
        load_config(path)


def test_load_config_not_object(tmp_path) -> None:
    path = tmp_path / 'arr.json'
    path.write_text('[1, 2, 3]', encoding='utf-8')
    with pytest.raises(ConfigError):
        load_config(path)
