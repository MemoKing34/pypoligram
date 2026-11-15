from __future__ import annotations

from typing import TYPE_CHECKING

import pyrogram

import pypoligram
from pypoligram.filters import ALL

from .unbound_arguments import unbound_arguments

if TYPE_CHECKING:
	from collections.abc import Callable

	from pyrogram.methods.decorators.handler_type import HandlerType

	from pypoligram.filters import Filter as PFilter


class OnStop:
	def on_stop(
		self: OnStop | PFilter | None = None,
		client_filters: PFilter | None = None,
	) -> Callable[[HandlerType], HandlerType]:
		"""Decorator for handling client stop.

		This does the same thing as :meth:`~pypoligram.ClientManager.add_handler` using the
		:obj:`~pyrogram.handlers.StopHandler`.

		Parameters:
			client_filters (:obj:`~pypoligram.filters`, *optional*):
				Pass one or more filters to allow only a subset of clients to be passed
				in your function.
		"""

		def decorator(func: HandlerType) -> HandlerType:
			arguments = unbound_arguments(
				self,
				client_filters=client_filters,
				filters=None,
				group=0,
			)
			handler = pyrogram.handlers.StopHandler(func)

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
