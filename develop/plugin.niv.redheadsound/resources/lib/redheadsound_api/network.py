# import sys
# import os

# parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(1, os.path.join(parent_dir, 'external_libraries'))

from external_libraries.httpx import Client, HTTPStatusError
from external_libraries.httpx import TimeoutException, ConnectError, RequestError, HTTPError
from time import time, sleep

#from ado.config import HTTPClientConfig

HEADERS: dict = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36',
}

# def set_headers(headers):
#     """
#     Функция для обновления заголовков без дополнительной передачи в класс.

#     :param headers: headers | dict
#     """
#     HEADERS.clear()
#     HEADERS.update(headers)

class BaseClient:
    """
    Базовый клиент для выполнения HTTP-запросов.

    Этот класс предоставляет основные методы для выполнения HTTP-запросов 
    (GET, POST, PATCH, DELETE) и использует httpx.Client для выполнения 
    запросов.
    """

    def __init__(self, **kwargs):
        self.kwargs = {
            'base_url': '',
            'headers': None,
            'timeout': 5,
            'proxy': None,
            'verify': True,
            'redirect': True,
            'http2': True,
            'http1': False,
            'sleep': 5
            }
        self.kwargs.update(kwargs)

        self.client = Client(
            headers = self.kwargs['headers'] or HEADERS,
            follow_redirects=self.kwargs['redirect'],
            timeout=self.kwargs['timeout'],
            http1=self.kwargs['http1'],
            http2=self.kwargs['http2'],
            verify=self.kwargs['verify'],
            proxy=self.kwargs['proxy'],
            base_url=self.kwargs['base_url']
            )

        self.sleep = self.kwargs['sleep']

    def client_get(self, url: str, params: dict = None, retry: int = 2) -> dict:
        """
        Выполняет GET-запрос.

        :param url: основной url если нет base_url
        :param params: параметры запроса
        :param retry: количество повторных запросов
        :return: dict 
        """
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            result = {
                    'status': response.status_code,
                    'reason': response.reason_phrase,
                    'encoding': response.encoding,
                    'response': response,
                    'error': None
                }
        except HTTPStatusError as exc:
            result = {
                'reason': f"{exc.request.url}",
                'error': exc.response.status_code
                }
        except ConnectError:
            result = {
                'reason': f"{url}",
                'error': 'ConnectError'
                }
        except TimeoutException:
            result = {
                'reason': f"{url}",
                'error': 'TimeoutException'
                }

        if result['error']:
            if retry:
                sleep(self.sleep)
                return self.client_get(url=url, params=params, retry=retry - 1)

        return result

    def client_post(self, url: str, data: dict = None, retry: int = 2) -> dict:
        """
        Выполняет POST-запрос.

        :param url: основной url если нет base_url
        :param data: параметры post запроса
        :param retry: количество повторных запросов
        :return: dict 
        """
        try:
            response = self.client.post(url, data=data)
            response.raise_for_status()
            result = {
                    'status': response.status_code,
                    'reason': response.reason_phrase,
                    'encoding': response.encoding,
                    'response': response,
                    'error': None
                }
        except HTTPStatusError as exc:
            result = {
                'reason': f"{exc.request.url}",
                'error': exc.response.status_code
                }
        except ConnectError:
            result = {
                'reason': f"{url}",
                'error': 'ConnectError'
                }
        except TimeoutException:
            result = {
                'reason': f"{url}",
                'error': 'TimeoutException'
                }

        if result['error']:
            if retry:
                sleep(self.sleep)
                return self.client_post(url=url, data=data, retry=retry - 1)

        return result

    def client_download(self,
                 url: str,
                 output_file: str,
                 method: str = "GET",
                 data: dict = None
                 ) -> dict:
        """
        Выполняет Загрузку файла.

        :param url: основной url если нет base_url
        :param output_file: полный путь для сохранения файла
        :param method: тип запроса GET, POST
        :param data: параметры запроса
        :return: dict  
        """
        result: dict = None

        try:
            with self.client.stream(method=method, url=url, data=data) as response:
                response.raise_for_status()
                with open(output_file, "wb") as file:
                    for chunk in response.iter_bytes():
                        file.write(chunk)
                result = {
                    'reason': "File download succeeded",
                    'error': None
                    }
        except HTTPStatusError as exc:
            result = {
                'reason': f"{exc.request.url}",
                'error': exc.response.status_code
                }
        except ConnectError:
            result = {
                'reason': f"{url}",
                'error': 'ConnectError'
                }
        except TimeoutException:
            result = {
                'reason': f"{url}",
                'error': 'TimeoutException'
                }

        return result

    def client_close(self):
        """
        Закрывает запрос
        """
        self.client.close()

# def http_client(
#     base_url: URL | str = '',
#     headers: dict = None,
#     timeout: int = 5,
#     proxy: str = None,
#     verify: bool = True,
#     redirect: bool = True,
#     http2: bool = True,
#     http1: bool = False
#     ) -> Client:
#     """
#     Функция для инициализации HTTP-клиента.

#     :return: Экземпляр httpx.Client
#     """
#     return Client(
#         headers = headers or HEADERS,
#         follow_redirects=redirect,
#         timeout=timeout, # Таймаут для всех запросов
#         http1=http1,
#         http2=http2,
#         verify=verify,
#         proxy=proxy,
#         base_url=base_url,  # Базовый URL для API
#     )
