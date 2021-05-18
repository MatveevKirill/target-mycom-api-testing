import os
import requests

from urllib.parse import urljoin

from api.common.base_client import APIClientBase
from api.common.methods import APIMethods
from api.common.exceptions import *


class TargetAPIClient(APIClientBase):

    def get_csrf_token(self) -> str:

        cookies = self._request(
            urljoin(self.base_url, "csrf/"),
            jsonify=False
        ).headers['set-cookie'].split(";")
        csrf_token = [c for c in cookies if 'csrftoken' in c]

        if not cookies:
            raise CannotGetCSRFToken("CSRF token not found.")

        csrf_token = csrf_token[0].split('=')[-1]
        return csrf_token

    def get_campaign(self, campaign_id: int) -> dict:
        return self._request(urljoin(self.base_url, f"api/v2/campaigns/{campaign_id}.json?fields=id,name,status"))

    def get_campaign_url_id(self, get_url: str):
        url = urljoin(self.base_url, f'api/v1/urls/?url={get_url}')

        try:
            return self._request(url)['id']
        except KeyError:
            raise CannotGetJSONAttribute(f"For url='{url}' not had field 'id'.")

    def get_segment(self, segment_id: int = None) -> dict:

        response = self._request(urljoin(self.base_url, 'api/v2/remarketing/segments.json?fields=id,name'))

        if segment_id is None:
            return response
        else:
            for item in response['items']:
                if item['id'] == segment_id:
                    return item
        raise ObjectNotFoundError(f"Segment with id '{segment_id}' does not exist.")

    def get_image(self, id_mediateka: int, expected_status: int = 200, jsonify: bool = True):
        return self._request(
            urljoin(self.base_url, f'api/v2/mediateka/{id_mediateka}.json'),
            expected_status=expected_status,
            jsonify=jsonify
        )

    def post_login(self, username: str, password: str) -> requests.Response:
        url = "https://auth-ac.my.com/auth"

        headers = {
            'Referer': self.base_url
        }

        post_data = {
            "email": username,
            "password": password,
            "continue": "https://target.my.com/auth/mycom?state=target_login%3D1%26ignore_opener%3D1#email",
            "failure": "https://account.my.com/login/"
        }

        response = self._request(url, method=APIMethods.POST, headers=headers, data=post_data, jsonify=False)

        # Проверяем на наличие 'mc', 'ssdc', 'mrcu', 'sdcs', 'z'. которые устанавливаются в процессе авторизации.
        for c in ['mc', 'ssdc', 'mrcu', 'sdcs', 'z']:
            if self.session.cookies.get(c) is None:
                raise IncorrectLoginException(f"Cannot got cookie: '{c}'.")

        # Получаем csrf-токен и устанавливаем автоматически в cookie.
        self.get_csrf_token()

        return response

    def post_create_campaign(self, campaign_data: dict) -> dict:
        url = urljoin(self.base_url, "/api/v2/campaigns.json")

        headers = {
            'Content-Type': 'application/json',
            "X-CSRFToken": self.session.cookies.get("csrftoken")
        }

        return self._request(url, method=APIMethods.POST, headers=headers, json=campaign_data)

    def post_send_image(self, file_path: str) -> dict:
        url_static = urljoin(self.base_url, 'api/v2/content/static.json')

        mime_type = file_path.split(os.sep)[-1].split('.')[-1]

        if mime_type not in ["png", "jpg"]:
            raise InvalidMimeType(f"Cannot use mime type '{mime_type}'. Allowed: png, jpg.")

        headers = {
            'X-CSRFToken': self.session.cookies.get('csrftoken')
        }

        files_static = {
            'width': (None, 0),
            'height': (None, 0),
            'file': ('img.jpg', open(file_path, 'rb'), f'image/{mime_type}')
        }

        response_static = self._request(
            url_static,
            method=APIMethods.POST,
            headers=headers,
            files=files_static,
            jsonify=False
        )

        try:
            id_static = response_static.json()['id']
        except KeyError:
            raise CannotGetJSONAttribute(f'There is no json key "id" on "{url_static}".')

        # Отправляем данные в Mediateka.
        headers['Content-Type'] = 'application/json'
        url_mediateka = urljoin(self.base_url, 'api/v2/mediateka.json')

        json_data = {
            'content': {
                "id": id_static
            },
            'description': file_path.split(os.sep)[-1]
        }

        response_mediateka = self._request(
            url_mediateka,
            method=APIMethods.POST,
            headers=headers,
            json=json_data,
            jsonify=False,
            expected_status=201
        )

        try:
            id_mediateka = response_mediateka.json()['id']
        except KeyError:
            raise CannotGetJSONAttribute(f'There is no json key "id" on "{url_mediateka}".')

        return {
            'id_static': id_static,
            'id_mediateka': id_mediateka
        }

    def post_create_segment(self, segment_data: dict) -> dict:
        url = urljoin(self.base_url, 'api/v2/remarketing/segments.json?fields=id,name')

        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': self.session.cookies.get('csrftoken')
        }

        return self._request(
            url,
            method=APIMethods.POST,
            headers=headers,
            json=segment_data
        )

    def delete_campaign(self, campaign_id: int) -> requests.Response:
        url = urljoin(self.base_url, f"api/v2/campaigns/{campaign_id}.json")

        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': self.session.cookies.get("csrftoken")
        }

        json_data = {
            "status": "deleted"
        }

        return self._request(
            url,
            method=APIMethods.POST,
            headers=headers,
            json=json_data,
            expected_status=204,
            jsonify=False
        )

    def delete_segment(self, segment_id: int) -> requests.Response:
        url = urljoin(self.base_url, f'api/v2/remarketing/segments/{segment_id}.json')

        headers = {
            'X-CSRFToken': self.session.cookies.get('csrftoken')
        }

        return self._request(
            url,
            method=APIMethods.DELETE,
            headers=headers,
            expected_status=204,
            jsonify=False
        )

    def delete_image(self, id_metateka: int) -> requests.Response:
        headers = {
            "X-CSRFToken": self.session.cookies.get('csrftoken')
        }

        return self._request(
            urljoin(self.base_url, f'api/v2/mediateka/{id_metateka}.json'),
            method=APIMethods.DELETE,
            headers=headers,
            expected_status=204,
            jsonify=False
        )
