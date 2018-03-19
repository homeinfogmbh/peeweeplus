"""Context managers."""

__all__ = ['ChangedConnection']


class ChangedConnection:
    """Sets the connection parameters of the
    target model to those of the source model.
    """

    def __init__(self, target, source):
        """Sets the models."""
        self.target = target
        self.source = source
        self._connection_parameters = None

    def __enter__(self):
        """Alters the connection parameters."""
        self._connection_parameters = self.target._meta.database.connect_params
        params = {
            key: value for key, value in
            self.target._meta.database.connect_params.items()}
        params.update(self.source._meta.database.connect_params)
        self.target._meta.database.connect_params = params
        return self

    def __exit__(self, *_):
        """Resets the connection parameters."""
        self.target._meta.database.connect_params = self._connection_parameters
