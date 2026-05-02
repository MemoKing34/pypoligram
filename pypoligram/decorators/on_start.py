from typing import Callable, Optional, Union

import pyrogram

import pypoligram
from pypoligram.filters import ALL
from pypoligram.filters import Filter as PFilter


class OnStart:
	def on_start(self: Optional[Union["OnStart", PFilter]] = None, client_filters: Optional[PFilter] = None) -> Callable:
		"""Decorator for handling client start.

		This does the same thing as :meth:`~pypoligram.ClientManager.add_handler` using the
		:obj:`~pyrogram.handlers.StartHandler`.

		Parameters:
			client_filters (:obj:`~pypoligram.filters`, *optional*):
				Pass one or more filters to allow only a subset of clients to be passed
				in your function.
		"""

		def decorator(func: Callable) -> Callable:
			nonlocal self, client_filters
			if isinstance(self, pypoligram.ClientManager):
				self.add_handler(pyrogram.handlers.StartHandler(func), client_filters or ALL)
			else:
				if not hasattr(func, "handlers"):
					func.handlers = []
				if isinstance(self, PFilter) or self is None:
					client_filters, self = self, client_filters

				func.handlers.append((pyrogram.handlers.StartHandler(func), 0))

			return func

		return decorator
