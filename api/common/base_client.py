import logging
import requests

from api.common.methods import APIMethods
from api.common.exceptions import *

MAX_RESPONSE_LENGTH = 500

logger = logging.getLogger('api-tests')


class APIClientBase(object):
    base_url: str = None
    session: requests.Session = requests.Session()

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def _request(
            self,
            url: str,
            method: str = APIMethods.GET,
            headers: dict = None,
            data: dict = None,
            params: dict = None,
            json: dict = None,
            files: dict = None,
            expected_status: int = 200,
            jsonify: bool = True,
            allow_redirects: bool = True
    ):
        self.log_prepare(url, headers, expected_status, json, data, files, params)
        response = self.session.request(
            method,
            url,
            headers=headers,
            data=data,
            params=params,
            json=json,
            allow_redirects=allow_redirects,
            files=files
        )
        self.log_post(response)

        if response.status_code != expected_status:
            raise ResponseStatusCodeException(
                f"Got {response.status_code} for URL '{url}'.\n"
                f"Response text: {response.text}.\n"
                f"Expected status code: {expected_status}.\n"
                f"Request URL: {response.request.url}.\n"
                f"Method: {method}.\n"
                f"Response headers: {response.headers}.\n"
                f"Request headers: {response.request.headers}.\n"
                f"Request cookies: {self.session.cookies}.\n"
                f"Send data: {data}.\n"
                f"Send json data: {json}.\n"
                f"Send files: {files}.\n"
                f"Allow redirects: {allow_redirects}."
            )

        if jsonify:
            return response.json()
        else:
            return response

    @staticmethod
    def log_prepare(
            url: str,
            headers: dict,
            expected_status: int,
            json: dict = None,
            data: dict = None,
            files: dict = None,
            params: dict = None
    ) -> None:
        logger.info(
            f'Performing request:\n'
            f'URL: {url}',
            f'HEADERS: {headers}\n'
            f'EXPECTED STATUS: {expected_status}\n'
            f'DATA: {data}\n'
            f'JSON DATA: {json}\n'
            f'FILES DATA: {files}\n'
            f'PARAMS DATA: {params}'
        )

    @staticmethod
    def log_post(response: requests.Response) -> None :
        log_str = f'\n---GOT RESPONSE---\n' \
                  f'RESPONSE STATUS: {response.status_code}'

        if len(response.text) > MAX_RESPONSE_LENGTH:
            if logger.level == logging.INFO:
                logger.info(f'{log_str}\n'
                            f'RESPONSE CONTENT: COLLAPSED due to response size > {MAX_RESPONSE_LENGTH}. '
                            f'Use DEBUG logging.\n\n')
            elif logger.level == logging.DEBUG:
                logger.debug(f'{log_str}\n'
                             f'RESPONSE CONTENT:\n'
                             f'{response.text}\n\n')
        else:
            logger.info(f'{log_str}\n'
                        f'RESPONSE CONTENT: {response.text}\n\n')
