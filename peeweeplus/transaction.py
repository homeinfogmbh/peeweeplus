"""Transactions for adding and deleting multiple records in one action."""

from collections import deque


__all__ = ['Transaction']


class Transaction(deque):
    """A Transaction."""

    def __init__(self):
        """Sets the primary record."""
        super().__init__()
        self.primary = None

    def __getattr__(self, attr):
        """Delegates to the primary record."""
        return getattr(self.primary, attr)

    def add(self, record, before=False, primary=False):
        """Adds the respective record."""
        item = (False, record)

        if primary:
            self.primary = record

        if before:
            return self.appendleft(item)

        return self.append(item)

    def delete(self, record, before=False):
        """Deletes the respective record."""
        item = (True, record)

        if before:
            return self.appendleft(item)

        return self.append(item)

    def save(self):
        """Saves the records or sub-transactions."""
        for delete, record in self:
            if delete:
                record.delete_instance()
            else:
                record.save()