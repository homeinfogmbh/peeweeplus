"""Extensions of the Model class."""

from typing import Iterator, NamedTuple, Union

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
    rel_model: ModelBase
    join_type: str
    condition: Expression


def get_foreign_keys(model: Union[ModelAlias, ModelBase]) \
        -> Iterator[ForeignKeyField]:
    """Yields foreign keys."""

    for attribute, field in (fields := model._meta.fields).items():
        if isinstance(field, ForeignKeyField):
            if attribute.endswith('_id') and attribute + '_id' not in fields:
                continue

            if isinstance(model, ModelAlias):
                model = model.model

            if field.rel_model is model:
                continue

            yield (attribute, field)


def join_tree(model: Union[ModelAlias, ModelBase]) -> Iterator[JoinCondition]:
    """Joins on all foreign keys."""

    for attribute, _ in get_foreign_keys(model):
        field = getattr(model, attribute)
        rel_model = field.rel_model.alias()
        join_type = JOIN.LEFT_OUTER #if field.null else JOIN.INNER
        condition = field == rel_model.id
        yield JoinCondition(model, rel_model, join_type, condition)
        yield from join_tree(rel_model)


def select_tree(model: ModelBase) -> ModelSelect:
    """Selects the entire relation tree."""

    tree = list(join_tree(model))
    select = model.select(model, *(jc.rel_model for jc in tree))

    for model_, rel_model, join_type, condition in tree:
        select = select.join_from(
            model_, rel_model, join_type=join_type, on=condition)

    return select
