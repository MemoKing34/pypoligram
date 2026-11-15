from __future__ import annotations

from typing import TYPE_CHECKING

import pyrogram

import pypoligram
from pypoligram.filters import ALL

from .unbound_arguments import unbound_arguments

if TYPE_CHECKING:
	from collections.abc import Callable

	from pyrogram.filters import Filter
	from pyrogram.methods.decorators.handler_type import HandlerType

	from pypoligram.filters import Filter as PFilter


class OnBusinessConnection:
	def on_business_connection(
		self: OnBusinessConnection | PFilter | Filter | None = None,
		client_filters: PFilter | Filter | None = None,
		filters: Filter | None = None,
		group: int = 0,
	) -> Callable[[HandlerType], HandlerType]:
		"""Decorator for handling changes in business connection.

		This does the same thing as :meth:`~pypoligram.ClientManager.add_handler` using the
		:obj:`~pyrogram.handlers.BusinessConnectionHandler`.

		Parameters:
			client_filters (:obj:`~pypoligram.filters`, *optional*):
				Pass one or more filters to allow only a subset of clients to be passed
				in your function.

			filters (:obj:`~pyrogram.filters`, *optional*):
				Pass one or more filters to allow only a subset of updates to be passed
				in your function.

			group (``int``, *optional*):
				The group identifier, defaults to 0.
		"""

		def decorator(func: HandlerType) -> HandlerType:
			arguments = unbound_arguments(
				self,
				client_filters=client_filters,
				filters=filters,
				group=group,
			)
			handler = pyrogram.handlers.BusinessConnectionHandler(
				func, arguments.filters
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
