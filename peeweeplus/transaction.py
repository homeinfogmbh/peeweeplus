"""Transactions for adding and deleting multiple records in one action."""

from collections import deque
from typing import NamedTuple

from peewee import Model


__all__ = ['Transaction']


class TransactionItem(NamedTuple):
    """Item of a transaction."""

    delete: bool
    record: Model


class Transaction(deque):
    """A Transaction."""

    def __init__(self):
        """Sets the primary record."""
        super().__init__()
        self.primary = None

    def __getattr__(self, attr):
        """Delegates to the primary record."""
        return getattr(self.primary, attr)

    def add(self, record: Model, left: bool = False, primary: bool = False):
        """Adds the respective record."""
        item = TransactionItem(False, record)

        if primary:
            self.primary = record

        if left:
            return self.appendleft(item)

        return self.append(item)

    def delete(self, record: Model, left: bool = False):
        """Deletes the respective record."""
        item = TransactionItem(True, record)

        if left:
            return self.appendleft(item)

        return self.append(item)

    def commit(self):
        """Saves the records or sub-transactions."""
        for item in self:
            if item.delete:
                item.record.delete_instance()
            else:
                item.record.save()
