from __future__ import annotations as _annotations

from collections.abc import Sequence
from dataclasses import dataclass

import pypoligram
from pyrogram.filters import Filter

from pypoligram.filters import Filter as PFilter

ExceptionsType = Exception | Sequence[Exception] | None


def _given(receiver: object, *values: object) -> tuple[object, ...]:
    """Drop the receiver when it is the manager instead of a shifted argument.

    A call on the class (`ClientManager.on_message(...)`) puts the first real argument
    in `receiver`; a call on an instance (`manager.on_message(...)`) puts the manager
    there instead. Only the first form is shifted.
    """
    if isinstance(receiver, pypoligram.ClientManager):
        return values
    return (receiver, *values)


@dataclass(frozen=True)
class UnboundArguments:
    client_filters: PFilter | None
    filters: Filter | None
    group: int


def unbound_arguments(
    receiver: object,
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
    for value in _given(receiver, client_filters, filters):
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


@dataclass(frozen=True)
class UnboundErrorArguments:
    exceptions: ExceptionsType
    client_filters: PFilter | None
    filters: Filter | None
    group: int


def unbound_error_arguments(
    receiver: object,
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
    given = _given(receiver, exceptions, client_filters, filters)
    exceptions = client_filters = filters = None

    for value in given:
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
