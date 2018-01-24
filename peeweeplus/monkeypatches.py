"""Monkey patches for peewee."""

from peewee import BaseModel

__all__ = ['getitem']


def _by_primary_key(model, pk_value):
    """Gets a record by its primary key."""

    return model.get(model._meta.primary_key == pk_value)


def getitem(enable=True):
    """Enables or disables getting records by
    primary keys values using the indexing syntax:

        try:
            record_with_pk_12 = Model[12]
        except DoesNotExist:
            print('No record with primary key 12.')
    """

    if enable:
        BaseModel.__getitem__ = _by_primary_key
    else:
        del BaseModel.__getitem__
