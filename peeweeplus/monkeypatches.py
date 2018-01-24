"""Monkey patches for peewee."""

from peewee import BaseModel

__all__ = ['getitem']


def _by_primary_key(model, pk_value):
    """Gets a record by its primary key."""

    return model.get(model._meta.primary_key == pk_value)


def getitem():
    """Enables getting records by primary
    keys using the following syntax:

        try:
            record_with_pk_12 = Model[12]
        except DoesNotExist:
            print('No record with primary key 12.')
    """
    BaseModel.__getitem__ = _by_primary_key
