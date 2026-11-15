from __future__ import annotations as _annotations

from dataclasses import dataclass
from collections.abc import Sequence

from pyrogram.filters import Filter
from pypoligram.filters import Filter as PFilter


@dataclass(frozen=True)
class UnboundArguments:
    client_filters: PFilter | None
    filters: Filter | None
    group: int


def unbound_arguments(
    receiver: PFilter | Filter | None,
    *,
    client_filters: PFilter | Filter | int | None,
    filters: Filter | int | None,
    group: int,
) -> UnboundArguments:
    """Read what `@ClientManager.on_*(...)` was given, whichever way it was written.

    An unbound call shifts every positional argument one slot to the left, so the same
    value can arrive in `receiver`, `client_filters` or `filters` depending on how many
    arguments were passed. Client filters, update filters and ints don't collide, so each
    value is bucketed by type instead of following the shift.
    """
    for value in (receiver, client_filters, filters):
        if isinstance(value, PFilter):
            client_filters = value
        elif isinstance(value, Filter):
            filters = value
        elif type(value) is int:
            group = value
    return UnboundArguments(
        client_filters if isinstance(client_filters, PFilter) else None,
        filters if isinstance(filters, Filter) else None,
        group,
    )

ExceptionsType = Exception | Sequence[Exception] | None


@dataclass(frozen=True)
class UnboundErrorArguments:
    exceptions: ExceptionsType
    client_filters: PFilter | None
    filters: Filter | None
    group: int


def unbound_error_arguments(
    receiver: ExceptionsType,
    *,
    exceptions: ExceptionsType | PFilter | Filter,
    client_filters: PFilter | Filter | int | None,
    filters: Filter | int | None,
    group: int,
) -> UnboundErrorArguments:
    """Read what `@ClientManager.on_error(...)` was given, whichever way it was written.

    An unbound call shifts every positional argument one slot to the left, so the same
    value can arrive in `receiver`, `exceptions`, `client_filters` or `filters` depending
    on how many arguments were passed. Client filters, update filters and ints don't
    collide, so each value is bucketed by type instead of following the shift; whatever
    is left is the exception type or instance.
    """
    _tuple = (receiver, exceptions, client_filters, filters)
    exceptions = client_filters = filters = None

    for value in _tuple:
        if isinstance(value, PFilter):
            client_filters = value
        elif isinstance(value, Filter):
            filters = value
        elif type(value) is int:
            group = value
        elif value is not None:
            exceptions = value

    return UnboundErrorArguments(
        exceptions,
        client_filters if isinstance(client_filters, PFilter) else None,
        filters if isinstance(filters, Filter) else None,
        group,
    )
