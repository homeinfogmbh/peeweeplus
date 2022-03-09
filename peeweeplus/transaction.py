"""Transactions for adding and deleting multiple records in one action."""

from collections import deque
from contextlib import ExitStack
from typing import Iterable, NamedTuple

from peewee import Database, Model


__all__ = ['Transaction']


class TransactionItem(NamedTuple):
    """Item of a transaction."""

    delete: bool
    record: Model


class AtomicTransaction(ExitStack):
    """Context manager for atomic transactions."""

    def __init__(self, databases: Iterable[Database]):
        super().__init__()
        self.databases = databases

    def __enter__(self):
        stack = super().__enter__()

        for database in self.databases:
            stack.enter_context(database.atomic())

        return stack

    def __exit__(self, exc_type, exc_val, exc_tb):
        for database in self.databases:
            database.close()

        return super().__exit__(exc_type, exc_val, exc_tb)


class Transaction(deque):
    """A Transaction."""

    def __init__(self):
        """Sets the primary record."""
        super().__init__()
        self.primary = None

    def __getattr__(self, attr):
        """Delegates to the primary record."""
        return getattr(self.primary, attr)

    @property
    def databases(self) -> set[Database]:
        """Returns a set of databases involved."""
        return {item.record._meta.database for item in self}

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
        with AtomicTransaction(self.databases):
            for item in self:
                if item.delete:
                    item.record.delete_instance()
                else:
                    item.record.save()
