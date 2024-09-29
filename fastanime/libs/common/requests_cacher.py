import atexit
import json
import logging
import os
import pathlib
import re
import sqlite3
import time
from datetime import datetime
from urllib.parse import urlencode

import requests

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
        cache_db_lock_file: str,
        max_lifetime: int = 604800,
        max_size: int = (1024**2) * 10,
        table_name: str = "fastanime_requests_cache",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.cache_db_path = cache_db_path
        self.max_lifetime = max_lifetime
        self.max_size = max_size
        self.table_name = table_name
        logger.debug("Acquiring lock on the db")
        self.acquirer_lock(cache_db_lock_file)
        logger.debug("Successfully acquired lock on the db")
        logger.debug("Getting connection to cache db")
        self.connection = sqlite3.connect(self.cache_db_path)
        logger.debug("Successfully gotten connection to cache db")

        logger.debug("Creating table if it does not exist")
        self.connection.cursor().execute(
            f"""
            create table if not exists {self.table_name!r} (
                url text, 
                status_code integer, 
                request_headers text, 
                response_headers text, 
                data blob,
                redirection_policy int,
                cache_expiry integer
            )""",
        )

        atexit.register(
            lambda connection: connection.commit() or connection.close(),
            self.connection,
        )

    def request(
        self,
        method,
        url,
        params=None,
        force_caching=False,
        fresh=False,
        *args,
        **kwargs,
    ):
        # do a new request without caching
        if fresh:
            logger.debug("Executing fresh request")
            return super().request(method, url, params=params, *args, **kwargs)

        # construct the exact url if it has params
        if params is not None:
            url += "?" + urlencode(params)

        redirection_policy = int(kwargs.get("force_redirects", False))

        # fetch cached request from database
        time_before_access_db = datetime.now()
        cursor = self.connection.cursor()
        logger.debug("Checking for existing request in cache db")
        cursor.execute(
            f"""
            select
                status_code,
                request_headers,
                response_headers,
                data,
                redirection_policy
            from {self.table_name!r}
            where
                url = ? 
                and redirection_policy = ? 
                and cache_expiry > ?
            """,
            (url, redirection_policy, int(time.time())),
        )
        cached_request = cursor.fetchone()
        time_after_access_db = datetime.now()

        # construct response from cached request
        if cached_request is not None:
            logger.debug("Found existing request in cache db")
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
            _request = requests.Request(
                method, url, headers=json.loads(request_headers), *args, **kwargs
            )
            response.request = _request.prepare()
            response.elapsed = time_after_access_db - time_before_access_db
            return response

        # construct a new response if the request does not already exist in the cache
        # cache the response provided conditions to cache are met
        response = super().request(method, url, *args, **kwargs)
        if response.ok and (
            force_caching
            or self.is_content_type_cachable(
                response.headers.get("content-type"), caching_mimetypes
            )
            and len(response.content) < self.max_size
        ):
            logger.debug("Caching current request")
            cursor.execute(
                f"insert into {self.table_name!r} values (?, ?, ?, ?, ?, ?, ?)",
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

            self.connection.commit()

        return response

    @staticmethod
    def is_content_type_cachable(content_type, caching_mimetypes):
        """Checks whether  the given encoding is supported by the cacher"""
        if content_type is None:
            return True

        mime, contents = content_type.split("/")

        contents = re.sub(r";.*$", "", contents)

        return mime in caching_mimetypes and any(
            content in caching_mimetypes[mime] for content in contents.split("+")
        )

    @staticmethod
    def acquirer_lock(lock_file: str):
        """the function creates a lock file preventing other instances of the cacher from running at the same time"""
        lockfile_path = pathlib.Path(lock_file)

        if lockfile_path.exists():
            with lockfile_path.open("r") as f:
                pid = f.read()

            raise RuntimeError(
                f"This instance of {__class__.__name__!r} is already running with PID: {pid}. "
                "Sqlite3 does not support multiple connections to the same database. "
                "If you are sure that no other instance of this class is running, "
                f"delete the lock file at {lockfile_path.as_posix()!r} and try again."
            )

        with lockfile_path.open("w") as f:
            f.write(str(os.getpid()))

        atexit.register(lockfile_path.unlink)


if __name__ == "__main__":
    with CachedRequestsSession("cache.db", "cache.lockfile") as session:
        response = session.get(
            "https://google.com",
        )

        response_b = session.get(
            "https://google.com",
        )

        print("A: ", response.elapsed)
        print("B: ", response_b.elapsed)

        print(response_b.text[0:30])
