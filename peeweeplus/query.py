"""Querying."""

from asyncio import coroutine, get_event_loop, sleep, wait

from peewee import DoesNotExist


__all__ = ['async_select', 'async_get']


@coroutine
def async_list(name, query):
    """Async list generator."""

    records = []

    for record in query:
        records.append(record)
        yield from sleep(0)

    return (name, records)


@coroutine
def async_lists(**queries):
    """Async generation of multiple lists."""

    tasks = [async_list(name, query) for name, query in queries.items()]
    return wait(tasks)


@coroutine
def async_return(name, query):
    """Async get query."""

    yield from sleep(0)

    try:
        return (name, query.get())
    except DoesNotExist:
        return (name, None)


@coroutine
def async_returns(**queries):
    """Async generation of multiple lists."""

    tasks = [async_return(name, query) for name, query in queries.items()]
    return wait(tasks)


def async_select(**queries):
    """Performs select queries in parallel."""

    loop = get_event_loop()
    tasks, _ = loop.run_until_complete(async_lists(**queries))
    return dict(task.result() for task in tasks)


def async_get(**queries):
    """Performs query.get() on multiple select queries in parallel."""

    loop = get_event_loop()
    tasks, _ = loop.run_until_complete(async_returns(**queries))
    return dict(task.result() for task in tasks)
