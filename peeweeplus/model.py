"""Extensions of the Model class."""

from typing import Iterator, NamedTuple

from peewee import JOIN
from peewee import Expression
from peewee import ForeignKeyField
from peewee import ModelAlias
from peewee import ModelBase
from peewee import ModelSelect


__all__ = ['select_tree']


class JoinCondition(NamedTuple):
    """Yields join conditions."""

    model: ModelBase
    rel_model: ModelAlias
    join_type: str
    condition: Expression


def get_foreign_keys(model: ModelBase) -> Iterator[ForeignKeyField]:
    """Yields foreign keys."""

    fields = model._meta.fields     # pylint: disable=W0212

    for attribute, field in fields.items():
        if isinstance(field, ForeignKeyField):
            if attribute.endswith('_id') and attribute + '_id' not in fields:
                continue

            if field.rel_model == model:
                continue

            yield field


def join_tree(model: ModelBase) -> Iterator[JoinCondition]:
    """Joins on all foreign keys."""

    for field in get_foreign_keys(model):
        rel_alias = field.rel_model.alias()
        join_type = JOIN.LEFT_OUTER if field.null else JOIN.INNER
        condition = field == rel_alias.id
        yield JoinCondition(model, rel_alias, join_type, condition)
        yield from join_tree(rel_alias)


def select_tree(model: ModelBase) -> ModelSelect:
    """Selects the entire relation tree."""

    tree = list(join_tree(model))
    select = model.select(model, *(jc.rel_alias for jc in tree))

    for model, rel_model, condition, join_type in tree:
        select = select.join_from(
            model, rel_model, join_type=join_type, on=condition)

    return select
