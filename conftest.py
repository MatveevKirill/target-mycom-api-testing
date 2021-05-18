import os
import shutil
import allure
import logging
import pytest
from _pytest.fixtures import Parser, FixtureRequest, Config

from creds import Credentials
from api.common.client import TargetAPIClient


def pytest_addoption(parser: Parser) -> None:
    parser.addoption("--debugging", action="store_true")


def pytest_configure(config: Config) -> None:
    base_test_dir = os.path.join(os.path.abspath(os.path.curdir), 'tmp', 'tests')

    if not hasattr(config, 'workerinput'):
        if os.path.exists(base_test_dir):
            shutil.rmtree(base_test_dir)
        os.makedirs(base_test_dir)

    config.base_test_dir = base_test_dir


@pytest.fixture(scope="session")
def credentials() -> tuple:
    creds = Credentials()
    return creds.LOGIN, creds.PASSWORD


@pytest.fixture(scope="session")
def configuration(request: FixtureRequest) -> dict:
    debugging = request.config.getoption('--debugging')


    return {
        "base_url": "https://target.my.com/",
        "debugging": debugging
    }


@pytest.fixture(scope="session")
def root_path() -> str:
    return os.path.abspath(os.path.curdir)


@pytest.fixture(scope="function")
def target_api_client(configuration: dict) -> TargetAPIClient:
    return TargetAPIClient(configuration['base_url'])


@pytest.fixture(scope="function")
def test_dir(root_path: str, request: FixtureRequest) -> str:
    test_name = request._pyfuncitem.nodeid.replace('/', '_').replace(':', '_')
    test_dir = os.path.join(request.config.base_test_dir, test_name)
    os.makedirs(test_dir)
    return test_dir


@pytest.fixture(scope='function', autouse=True)
def logger(test_dir: str, configuration: dict) -> logging.Logger:
    log_formatter = logging.Formatter('%(asctime)s - %(filename)-15s - %(levelname)-6s - %(message)s')
    log_file = os.path.join(test_dir, 'test.log')

    log_level = logging.DEBUG if configuration['debugging'] else logging.INFO

    file_handler = logging.FileHandler(log_file, 'w')
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(log_level)

    log = logging.getLogger('api-tests')
    log.propagate = False
    log.setLevel(log_level)
    log.handlers.clear()
    log.addHandler(file_handler)

    yield log

    for handler in log.handlers:
        handler.close()

    with open(log_file, 'r') as f:
        allure.attach(f.read(), 'test.log', attachment_type=allure.attachment_type.TEXT)
