import creds
import pytest

from api.common.exceptions import IncorrectLoginException
from test_api.base_test import APIBaseTest


class TestCaseTargetLogin(APIBaseTest):
    authorize: bool = False

    @pytest.mark.API
    def test_login_positive(self, credentials: tuple) -> None:
        # Авторизация на сервисе.
        self.target_api_client.post_login(credentials[0], credentials[1])

    @pytest.mark.API
    def test_login_negative(self) -> None:
        with pytest.raises(IncorrectLoginException):
            self.target_api_client.post_login("login@login.ru", "login")
            pytest.fail("The user was able to log in!")
