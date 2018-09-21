"""Querying."""

from asyncio import coroutine, get_event_loop, sleep, wait


__all__ = ['async_query']


@coroutine
def async_list(name, iterable):
    """Async list generator."""

    result = []

    for item in iterable:
        result.append(item)
        yield from sleep(0)

    return (name, result)


@coroutine
def async_jobs(queries):
    """Performs async jobs."""

    tasks = [async_list(name, query) for name, query in queries.items()]
    return wait(tasks)


def async_query(**queries):
    """Performs the provided queries in parallel."""

    loop = get_event_loop()
    tasks, _ = loop.run_until_complete(async_jobs(queries))
    return dict(task.result() for task in tasks)
