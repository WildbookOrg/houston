# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from unittest import mock

import pretend
import pytest

import app as target_module
from app import (
    _ensure_storage,
    configure_from_cli,
    configure_from_config_file,
    configure_using_houston_flask_config,
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

    def test_with_flask_config_name_param(self, monkeypatch):
        """must use the given name"""
        app = mock.MagicMock()
        monkeypatch.delenv('FLASK_CONFIG', raising=False)
        flask_config_name = 'testing'

        # Target
        configure_from_config_file(app, flask_config_name)

        expected_args = ('config.TestingConfig',)
        app.config.from_object.assert_called_with(*expected_args)

    def test_with_FLASK_CONFIG_envvar(self, monkeypatch):
        """must use the FLASK_CONFIG env-var"""
        app = mock.MagicMock()
        flask_config_name = 'testing'
        monkeypatch.setenv('FLASK_CONFIG', flask_config_name)

        # Target
        configure_from_config_file(app)  # note, no parameter

        expected_args = ('config.TestingConfig',)
        app.config.from_object.assert_called_with(*expected_args)

    def test_conflicting_flask_config(self, monkeypatch):
        """must raise AssertionError on conflicting names"""
        app = mock.MagicMock()
        flask_config_name = 'testing'
        monkeypatch.setenv('FLASK_CONFIG', 'production')

        # Target
        with pytest.raises(AssertionError) as exc_info:
            configure_from_config_file(app, flask_config_name)

        assert exc_info.match(r'.*both set and are not the same.')

    def test_invalid_flask_config_name(self, monkeypatch):
        """must raise KeyError with config name mapper"""
        app = mock.MagicMock()
        monkeypatch.delenv('FLASK_CONFIG', raising=False)
        flask_config_name = 'does-not-exists'

        # Target
        with pytest.raises(KeyError):
            configure_from_config_file(app, flask_config_name)

    @pytest.mark.parametrize('flask_config_name', ['local', 'testing'])
    def test_ImportError_in_flask_config(self, monkeypatch, flask_config_name):
        """must exit with returncode 1 on configuration importing issues"""
        sys_module = mock.MagicMock()
        monkeypatch.setattr(target_module, 'sys', sys_module)

        app = mock.MagicMock()
        monkeypatch.delenv('FLASK_CONFIG', raising=False)

        class TestException(Exception):
            pass

        # set app to raise ImportError
        app.config.from_object.side_effect = ImportError()
        # set 'sys.exit()' to raise a controlled error
        sys_module.exit.side_effect = TestException()

        # Target
        with pytest.raises(
            (
                ImportError,
                TestException,
            )
        ):
            configure_from_config_file(app, flask_config_name)

        if flask_config_name == 'local':
            # Check that we've logged an error
            app.logger.error.assert_called_once()


class TestConfigureFromCli:
    """Testing configure_from_cli"""

    def test_success(self):
        """must override any settings already in the config"""
        app = mock.MagicMock()
        app.config = {
            'foo': 'foo',
            'bar': 'bar',
            #: not overridden
            'baz': 'baz',
        }
        override = {
            'foo': 'oof',
            'bar': 'rab',
            #: completely new setting
            'smoo': 'ooms',
        }

        # Target
        configure_from_cli(app, override)

        # Test for overrides
        expected_config = override.copy()
        for k, v in app.config.items():
            expected_config.setdefault(k, v)
        assert app.config == expected_config

    def test_redacted(self, monkeypatch):
        """must redact sensative settings from the logs"""
        app = mock.MagicMock()
        app.config = {
            'EDM_AUTHENTICATIONS': 'foo',
        }
        override = {
            'EDM_AUTHENTICATIONS': 'bar',
        }

        # mock and patch logger usage
        log = mock.MagicMock()
        monkeypatch.setattr(target_module, 'log', log)

        # Target
        configure_from_cli(app, override)

        # Test for override
        expected_config = override.copy()
        for k, v in app.config.items():
            expected_config.setdefault(k, v)
        assert app.config == expected_config

        # Test for log redaction
        log.warning.assert_called_once()
        expected_log_snippet = "OVERRIDE: key='EDM_AUTHENTICATIONS' value='<REDACTED>'"
        # FIXME: python >= 3.8
        # assert expected_log_snippet in log.warning.call_args.args[0]
        assert expected_log_snippet in log.warning.call_args[0][0]


def test_configure_using_houston_flask_config():
    """must consume and replace the app config with a HoustonFlaskConfig instance"""
    app = mock.MagicMock()
    replaceable_config = {
        'FOO': 'bar',
        'BAR': 'baz',
    }
    app.config = replaceable_config

    # Target
    configure_using_houston_flask_config(app)

    from app.extensions.config import HoustonFlaskConfig

    assert isinstance(app.config, HoustonFlaskConfig)
    for key, value in replaceable_config.items():
        assert app.config[key] == value


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
