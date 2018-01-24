"""Monkey patches for peewee."""

from peewee import BaseModel

__all__ = ['monkeypatch']


def by_primary_key(model, pk_value):
    """Gets a record by its primary key."""

    return model.get(model._meta.primary_key == pk_value)


def monkeypatch(getitem=False):
    """Applies the respective monkey patches."""

    if getitem:
        # Enables:
        #     try:
        #         record_with_pk_12 = Model[12]
        #     except DoesNotExist:
        #         print('No record with primary key 12.')
        BaseModel.__getitem__ = by_primary_key
