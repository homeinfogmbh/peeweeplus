"""Context managers."""

from typing import Type

from peewee import Database, Model

from peeweeplus.dbproxy import DatabaseProxy


__all__ = ["ChangedConnection"]


def get_database(model: Type[Model]) -> Database:
    """Returns the respective database."""

    if isinstance((database := model._meta.database), DatabaseProxy):
        return database._database

    return database


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
