import pytest

from api.common.client import TargetAPIClient
from utils.builder import Builder


class APIBaseTest(object):
    authorize: bool = True

    target_api_client: TargetAPIClient = None
    builder: Builder = None

    @pytest.fixture(scope='function', autouse=True)
    def setup(self, target_api_client: TargetAPIClient, credentials: tuple) -> None:

        # Установить свойства.
        self.target_api_client = target_api_client
        self.builder = Builder()

        if self.authorize:
            self.target_api_client.post_login(credentials[0], credentials[1])

        yield

        # Очистка куки-файлов сессии.
        self.target_api_client.session.cookies.clear()
