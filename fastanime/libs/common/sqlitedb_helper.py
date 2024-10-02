import logging
import sqlite3
import time

logger = logging.getLogger(__name__)


class SqliteDB:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        logger.debug("Enabling WAL mode for concurrent access")
        self.connection.execute("PRAGMA journal_mode=WAL;")
        self.connection.close()
        self.connection = None

    def __enter__(self):
        logger.debug("Starting new connection...")
        start_time = time.time()
        self.connection = sqlite3.connect(self.db_path)
        logger.debug(
            "Successfully got a new connection in {} seconds".format(
                time.time() - start_time
            )
        )
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            logger.debug("Closing connection to cache db")
            self.connection.commit()
            self.connection.close()
            self.connection = None
            logger.debug("Successfully closed connection to cache db")
