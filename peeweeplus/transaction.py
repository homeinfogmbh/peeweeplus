"""Transaction handling."""


__all__ = ['Transaction']


class Transaction(list):
    """Transaction, containing multiple records."""

    def save(self, force_insert=False, only=None):
        """Saves the records."""
        for record in self:
            record.save(force_insert=force_insert, only=only)
