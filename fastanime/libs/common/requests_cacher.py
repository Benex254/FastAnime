import json
import logging
import re
import time
from datetime import datetime
from urllib.parse import urlencode

import requests

from .sqlitedb_helper import SqliteDB

logger = logging.getLogger(__name__)

caching_mimetypes = {
    "application": {
        "json",
        "xml",
        "x-www-form-urlencoded",
        "x-javascript",
        "javascript",
    },
    "text": {"html", "css", "javascript", "plain", "xml", "xsl", "x-javascript"},
}


class CachedRequestsSession(requests.Session):
    __request_functions__ = (
        "get",
        "options",
        "head",
        "post",
        "put",
        "patch",
        "delete",
    )

    def __new__(cls, *args, **kwargs):
        def caching_params(name: str):
            def wrapper(self, *args, **kwargs):
                return cls.request(self, name, *args, **kwargs)

            return wrapper

        for func in cls.__request_functions__:
            setattr(cls, func, caching_params(func))

        return super().__new__(cls)

    def __init__(
        self,
        cache_db_path: str,
        max_lifetime: int = 604800,
        max_size: int = (1024**2) * 10,
        table_name: str = "fastanime_requests_cache",
        clean_db=False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.cache_db_path = cache_db_path
        self.max_lifetime = max_lifetime
        self.max_size = max_size
        self.table_name = table_name
        self.sqlite_db_connection = SqliteDB(self.cache_db_path)

        # Prepare the cache table if it doesn't exist
        self._create_cache_table()

    def _create_cache_table(self):
        """Create cache table if it doesn't exist."""
        with self.sqlite_db_connection as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    url TEXT, 
                    status_code INTEGER, 
                    request_headers TEXT, 
                    response_headers TEXT, 
                    data BLOB,
                    redirection_policy INT,
                    cache_expiry INTEGER
                )"""
            )

    def request(
        self,
        method,
        url,
        params=None,
        force_caching=False,
        fresh=0,
        *args,
        **kwargs,
    ):
        # TODO: improve the caching functionality and add a layer to auto delete
        # expired requests
        if fresh:
            logger.debug("Executing fresh request")
            return super().request(method, url, params=params, *args, **kwargs)

        if params:
            url += "?" + urlencode(params)

        redirection_policy = int(kwargs.get("force_redirects", False))

        with self.sqlite_db_connection as conn:
            cursor = conn.cursor()
            time_before_access_db = datetime.now()

            logger.debug("Checking for existing request in cache")
            cursor.execute(
                f"""
                SELECT
                    status_code,
                    request_headers,
                    response_headers,
                    data,
                    redirection_policy
                FROM {self.table_name}
                WHERE
                    url = ? 
                    AND redirection_policy = ? 
                    AND cache_expiry > ?
                """,
                (url, redirection_policy, int(time.time())),
            )
            cached_request = cursor.fetchone()
            time_after_access_db = datetime.now()

            if cached_request:
                logger.debug("Found existing request in cache")
                (
                    status_code,
                    request_headers,
                    response_headers,
                    data,
                    redirection_policy,
                ) = cached_request

                response = requests.Response()
                response.headers.update(json.loads(response_headers))
                response.status_code = status_code
                response._content = data

                if "timeout" in kwargs:
                    kwargs.pop("timeout")
                if "headers" in kwargs:
                    kwargs.pop("headers")
                _request = requests.Request(
                    method, url, headers=json.loads(request_headers), *args, **kwargs
                )
                response.request = _request.prepare()
                response.elapsed = time_after_access_db - time_before_access_db

                return response

            # Perform the request and cache it
            response = super().request(method, url, *args, **kwargs)
            if response.ok and (
                force_caching
                or self.is_content_type_cachable(
                    response.headers.get("content-type"), caching_mimetypes
                )
                and len(response.content) < self.max_size
            ):
                logger.debug("Caching the current request")
                cursor.execute(
                    f"""
                    INSERT INTO {self.table_name} 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        url,
                        response.status_code,
                        json.dumps(dict(response.request.headers)),
                        json.dumps(dict(response.headers)),
                        response.content,
                        redirection_policy,
                        int(time.time()) + self.max_lifetime,
                    ),
                )

            return response

    @staticmethod
    def is_content_type_cachable(content_type, caching_mimetypes):
        """Checks whether the given encoding is supported by the cacher"""
        if content_type is None:
            return True

        mime, contents = content_type.split("/")

        contents = re.sub(r";.*$", "", contents)

        return mime in caching_mimetypes and any(
            content in caching_mimetypes[mime] for content in contents.split("+")
        )


if __name__ == "__main__":
    with CachedRequestsSession("cache.db") as session:
        response = session.get(
            "https://google.com",
        )

        response_b = session.get(
            "https://google.com",
        )

        print("A: ", response.elapsed)
        print("B: ", response_b.elapsed)

        print(response_b.text[0:30])
