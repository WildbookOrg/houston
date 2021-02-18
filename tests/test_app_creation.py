# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from unittest import mock

import pretend
import pytest

import app as target_module
from app import (
    _ensure_storage,
    CONFIG_NAME_MAPPER,
    configure_from_config_file,
    create_app,
)


class TestEnsureStorage:
    """Tests _ensure_storage"""

    def make_paths(self, tmp_path):
        return {
            'PROJECT_DATABASE_PATH': tmp_path / 'sql',
            'SUBMISSIONS_DATABASE_PATH': tmp_path / 'sub',
            'ASSET_DATABASE_PATH': tmp_path / 'ass',
        }

    def test_without_app(self, tmp_path, monkeypatch):
        # Stub values to isolate the test
        paths = self.make_paths(tmp_path)
        BaseConfig = pretend.stub(**{k: str(v) for k, v in paths.items()})
        monkeypatch.setattr(target_module, 'BaseConfig', BaseConfig)

        # Target
        _ensure_storage()

        for path in paths.values():
            assert path.exists()

    def test_with_app(self, tmp_path, monkeypatch):
        paths = self.make_paths(tmp_path)
        config = {k: str(v) for k, v in paths.items()}
        app = pretend.stub(config=config)

        # Target
        _ensure_storage(app)

        for path in paths.values():
            assert path.exists()


class TestConfigureFromConfigFile:
    """Tests configure_from_config_file"""

    def test_without_flask_config_definition(self, monkeypatch):
        """must defaults to 'local' without the flask config name"""
        app = mock.MagicMock()
        monkeypatch.delenv('FLASK_CONFIG', raising=False)

        # Target
        configure_from_config_file(app)

        expected_args = ('local_config.LocalConfig',)
        app.config.from_object.assert_called_with(*expected_args)


def test_create_app():
    try:
        create_app(testing=True)
    except SystemExit:
        # Clean git repository doesn't have `local_config.py`, so it is fine
        # if we get SystemExit error.
        pass


@pytest.mark.parametrize('flask_config_name', ['production', 'development', 'testing'])
def test_create_app_passing_flask_config_name(monkeypatch, flask_config_name):
    if flask_config_name == 'production':
        from config import ProductionConfig

        monkeypatch.setattr(ProductionConfig, 'SQLALCHEMY_DATABASE_URI', 'sqlite://')
        monkeypatch.setattr(ProductionConfig, 'SECRET_KEY', 'secret', raising=False)
    create_app(flask_config_name=flask_config_name, testing=True)


@pytest.mark.parametrize('flask_config_name', ['production', 'development', 'testing'])
def test_create_app_passing_FLASK_CONFIG_env(monkeypatch, flask_config_name):
    monkeypatch.setenv('FLASK_CONFIG', flask_config_name)
    if flask_config_name == 'production':
        from config import ProductionConfig

        monkeypatch.setattr(ProductionConfig, 'SQLALCHEMY_DATABASE_URI', 'sqlite://')
        monkeypatch.setattr(ProductionConfig, 'SECRET_KEY', 'secret', raising=False)
    create_app(testing=True)


def test_create_app_with_conflicting_config(monkeypatch):
    monkeypatch.setenv('FLASK_CONFIG', 'production')
    with pytest.raises(AssertionError):
        create_app('development', testing=True)


def test_create_app_with_non_existing_config():
    with pytest.raises(KeyError):
        create_app('non-existing-config', testing=True)


def test_create_app_with_broken_import_config():
    CONFIG_NAME_MAPPER['broken-import-config'] = 'broken-import-config'
    with pytest.raises(ImportError):
        create_app('broken-import-config', testing=True)
    del CONFIG_NAME_MAPPER['broken-import-config']
