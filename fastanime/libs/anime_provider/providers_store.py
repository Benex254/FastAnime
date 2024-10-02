import json
import logging
import time

logger = logging.getLogger(__name__)


class ProviderStoreDB:
    def __init__(
        self,
        provider_name,
        cache_db_path: str,
        max_lifetime: int = 604800,
        max_size: int = (1024**2) * 10,
        table_name: str = "fastanime_providers_store",
        clean_db=False,
    ):
        from ..common.sqlitedb_helper import SqliteDB

        self.cache_db_path = cache_db_path
        self.clean_db = clean_db
        self.provider_name = provider_name
        self.max_lifetime = max_lifetime
        self.max_size = max_size
        self.table_name = table_name
        self.sqlite_db_connection = SqliteDB(self.cache_db_path)

        # Prepare the cache table if it doesn't exist
        self._create_store_table()

    def _create_store_table(self):
        """Create cache table if it doesn't exist."""
        with self.sqlite_db_connection as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT, 
                    data_type TEXT,
                    provider_name TEXT, 
                    data TEXT, 
                    cache_expiry INTEGER
                )"""
            )

    def get(self, id: str, data_type: str, default=None):
        with self.sqlite_db_connection as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT
                    data
                FROM {self.table_name}
                WHERE
                    id = ?
                    AND data_type = ?
                    AND provider_name = ? 
                    AND cache_expiry > ?
                """,
                (id, data_type, self.provider_name, int(time.time())),
            )
            cached_data = cursor.fetchone()

            if cached_data:
                logger.debug("Found existing request in cache")
                (json_data,) = cached_data
                return json.loads(json_data)
        return default

    def set(self, id: str, data_type: str, data):
        with self.sqlite_db_connection as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"""
                INSERT INTO {self.table_name} 
                VALUES ( ?, ?,?, ?, ?)
                """,
                (
                    id,
                    data_type,
                    self.provider_name,
                    json.dumps(data),
                    int(time.time()) + self.max_lifetime,
                ),
            )


class ProviderStoreMem:
    def __init__(self) -> None:
        from collections import defaultdict

        self._store = defaultdict(dict)

    def get(self, id: str, data_type: str, default=None):
        return self._store[id][data_type]

    def set(self, id: str, data_type: str, data):
        self._store[id][data_type] = data


def ProviderStore(store_type, *args, **kwargs):
    if store_type == "persistent":
        return ProviderStoreDB(*args, **kwargs)
    else:
        return ProviderStoreMem()


if __name__ == "__main__":
    store = ProviderStore("persistent", "test_provider", "provider_store")
    store.set("123", "test", {"hello": "world"})
    print(store.get("123", "test"))
    print("-------------------------------")
    store = ProviderStore("memory")
    store.set("1", "test", {"hello": "world"})
    print(store.get("1", "test"))
