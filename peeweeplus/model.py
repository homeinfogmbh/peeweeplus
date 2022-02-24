"""Extensions of the Model class."""

from typing import Iterator, NamedTuple, Type, Union

from peewee import JOIN
from peewee import Expression
from peewee import ForeignKeyField
from peewee import Model
from peewee import ModelAlias
from peewee import Select


__all__ = ['select_tree']


ModelType = Union[ModelAlias, Type[Model]]


class JoinCondition(NamedTuple):
    """Yields join conditions."""

    model: ModelType
    rel_model: ModelType
    join_type: str
    condition: Union[bool, Expression]


def get_foreign_keys(model: ModelType) -> Iterator[str]:
    """Yields foreign key field attributes."""

    for attribute, field in (fields := model._meta.fields).items():
        if not isinstance(field, ForeignKeyField):
            continue

        if attribute.endswith('_id') and attribute + '_id' not in fields:
            continue

        if isinstance(model, ModelAlias):
            model = model.model

        if field.rel_model is model:
            continue

        yield attribute


def join_tree(model: ModelType) -> Iterator[JoinCondition]:
    """Joins on all foreign keys."""

    for attribute in get_foreign_keys(model):
        field = getattr(model, attribute)
        rel_model = field.rel_model.alias()
        join_type = JOIN.LEFT_OUTER if field.null else JOIN.INNER
        condition = field == rel_model.id
        yield JoinCondition(model, rel_model, join_type, condition)
        yield from join_tree(rel_model)


def select_tree(model: ModelType) -> Select:
    """Selects the entire relation tree."""

    tree = list(join_tree(model))
    select = model.select(model, *(condition.rel_model for condition in tree))

    for model_, rel_model, join_type, condition in tree:
        select = select.join_from(
            model_, rel_model, join_type=join_type, on=condition
        )

    return select
