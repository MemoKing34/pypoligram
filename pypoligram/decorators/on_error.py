from __future__ import annotations

from typing import TYPE_CHECKING

import pyrogram

import pypoligram
from pypoligram.filters import ALL

from .unbound_arguments import unbound_error_arguments

if TYPE_CHECKING:
	from collections.abc import Callable, Sequence

	from pyrogram.filters import Filter
	from pyrogram.methods.decorators.handler_type import HandlerType

	from pypoligram.filters import Filter as PFilter


class OnError:
	def on_error(
		self: OnError | Exception | Sequence[Exception] | PFilter | Filter | None = None,
		exceptions: Exception | Sequence[Exception] | None = None,
		client_filters: PFilter | Filter | None = None,
		filters: Filter | None = None,
		group: int = 0,
	) -> Callable[[HandlerType], HandlerType]:
		"""Decorator for handling unexpected errors.

		This does the same thing as :meth:`~pypoligram.ClientManager.add_handler` using the
		:obj:`~pyrogram.handlers.ErrorHandler`.

		Parameters:
			exceptions (``Exception`` | List of ``Exception``, *optional*):
				An exception type or a sequence of exception types that this handler should handle.
				If None, the handler will catch any exception that is a subclass of ``Exception``.

			client_filters (:obj:`~pypoligram.filters`, *optional*):
				Pass one or more filters to allow only a subset of clients to be passed
				in your function.

			filters (:obj:`~pyrogram.filters`, *optional*):
				Pass one or more filters to allow only a subset of errors to be passed
				in your function.

			group (``int``, *optional*):
				The group identifier, defaults to 0.
		"""

		def decorator(func: HandlerType) -> HandlerType:
			arguments = unbound_error_arguments(
				self,
				exceptions=exceptions,
				client_filters=client_filters,
				filters=filters,
				group=group,
			)
			handler = pyrogram.handlers.ErrorHandler(
				func, arguments.exceptions, arguments.filters
			)

			if isinstance(self, pypoligram.ClientManager):
				self.add_handler(
					handler, arguments.client_filters or ALL, arguments.group
				)
			else:
				if not hasattr(func, "handlers"):
					func.handlers = []

				func.handlers.append(
					(handler, arguments.client_filters or ALL, arguments.group)
				)

			return func

		return decorator
