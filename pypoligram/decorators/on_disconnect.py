from collections.abc import Callable
from typing import Union

import pyrogram

import pypoligram
from pypoligram.filters import ALL
from pypoligram.filters import Filter as PFilter


class OnDisconnect:
	def on_disconnect(self: Union["OnDisconnect", PFilter, None] = None, client_filters: PFilter | None = None):
		"""Decorator for handling disconnections.
  
		This does the same thing as :meth:`~pypoligram.ClientManager.add_handler` using the
		:obj:`~pyrogram.handlers.DisconnectHandler`.
  
		Parameters:
			client_filters (:obj:`~pypoligram.filters`, *optional*):
				Pass one or more filters to allow only a subset of clients to be passed
				in your function.
		"""

		def decorator(func: Callable) -> Callable:
			nonlocal self, client_filters
			if isinstance(self, pypoligram.ClientManager):
				self.add_handler(pyrogram.handlers.DisconnectHandler(func), client_filters or ALL)
			else:
				if not hasattr(func, "handlers"):
					func.handlers = []
				if isinstance(self, PFilter) or self is None:
					client_filters, self = self, client_filters

				func.handlers.append((pyrogram.handlers.DisconnectHandler(func), client_filters or ALL, 0))

			return func

		return decorator
