"""Context managers."""

from contextlib import contextmanager
from typing import Iterator, Type, Union

from peewee import Database, Model

from peeweeplus.dbproxy import DatabaseProxy


__all__ = ["ChangedConnection", "connected"]


def get_database(model: Type[Model]) -> Database:
    """Returns the respective database."""

    if isinstance((database := model._meta.database), DatabaseProxy):
        return database._database

    return database


@contextmanager
def connected(*databases: Union[Database, DatabaseProxy]) -> Iterator[None]:
    """Keep one connection per database open for the enclosed block.

    All queries inside the block reuse that connection instead of
    connecting for each query. Usable as context manager or decorator:

        with connected(DATABASE):
            ...

        @connected(DATABASE)
        def handler():
            ...

    Reentrant: only connections opened here are closed on exit.
    """
    opened = []

    try:
        for database in databases:
            if database.is_closed():
                database.connect()
                opened.append(database)

        yield
    finally:
        for database in reversed(opened):
            if not database.is_closed():
                database.close()


class ChangedConnection:
    """Sets the connection parameters of the
    target model to those of the source model.
    """

    def __init__(self, target: Type[Model], source: Type[Model]):
        """Sets the models."""
        self.target = target
        self.source = source
        self._connection_parameters = None

    def __enter__(self):
        """Alters the connection parameters."""
        self._connection_parameters = self.target_db.connect_params
        params = dict(self.target_db.connect_params)  # Copy dictionary.
        params.update(self.source_db.connect_params)
        self.target_db.connect_params = params
        return self

    def __exit__(self, *_):
        """Resets the connection parameters."""
        self.target_db.connect_params = self._connection_parameters

    @property
    def target_db(self):
        """Returns the target's database."""
        return get_database(self.target)

    @property
    def source_db(self):
        """Returns the source's database."""
        return get_database(self.source)
