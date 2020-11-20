"""Context managers."""

from peewee import ModelBase


__all__ = ['ChangedConnection']


class ChangedConnection:
    """Sets the connection parameters of the
    target model to those of the source model.
    """

    def __init__(self, target: ModelBase, source: ModelBase):
        """Sets the models."""
        self.target = target
        self.source = source
        self._connection_parameters = None

    def __enter__(self):
        """Alters the connection parameters."""
        self._connection_parameters = self.target_db.connect_params
        params = dict(self.target_db.connect_params)    # Copy dictionary.
        params.update(self.source_db.connect_params)
        self.target_db.connect_params = params
        return self

    def __exit__(self, *_):
        """Resets the connection parameters."""
        self.target_db.connect_params = self._connection_parameters

    @property
    def target_db(self):
        """Returns the target's database."""
        return self.target._meta.database   # pylint: disable=W0212

    @property
    def source_db(self):
        """Returns the source's database."""
        return self.source._meta.database   # pylint: disable=W0212
