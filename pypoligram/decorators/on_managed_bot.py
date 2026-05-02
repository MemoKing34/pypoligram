from typing import Callable, Optional, Union

import pyrogram
from pyrogram.filters import Filter

import pypoligram
from pypoligram.filters import ALL
from pypoligram.filters import Filter as PFilter


class OnManagedBot:
	def on_managed_bot(
		self: Optional[Union["OnManagedBot", PFilter, Filter]] = None,
		client_filters: Optional[Union[PFilter, Filter]] = None,
		filters: Optional[Filter] = None,
		group: int = 0,
	) -> Callable:
		"""Decorator for handling new managed bot creation updates.

		This does the same thing as :meth:`~pypoligram.ClientManager.add_handler` using the
		:obj:`~pyrogram.handlers.ManagedBotUpdatedHandler`.

		Parameters:
			client_filters (:obj:`~pypoligram.filters`, *optional*):
				Pass one or more filters to allow only a subset of clients to be passed
				in your function.

			filters (:obj:`~pyrogram.filters`, *optional*):
				Pass one or more filters to allow only a subset of updates to be passed
				in your function.

			group (``int``, *optional*):
				The group identifier, defaults to 0.

		Parameters:
			client_filters (:obj:`~pypoligram.filters`, *optional*):
				Pass one or more filters to allow only a subset of clients to be passed
				in your function.
		"""

		def decorator(func: Callable) -> Callable:
			nonlocal self, client_filters, filters, group
			if isinstance(self, pypoligram.ClientManager):
				self.add_handler(pyrogram.handlers.ManagedBotUpdatedHandler(func, filters), client_filters or ALL, group)
			elif isinstance(self, Filter) or self is None:
				if not hasattr(func, "handlers"):
					func.handlers = []
				if isinstance(self, PFilter):
					client_filters, self = self, client_filters
				if isinstance(self, Filter):
					filters, self = self, filters
				if isinstance(self, int):
					group = self or 0

				func.handlers.append(
					(
						pyrogram.handlers.ManagedBotUpdatedHandler(func, filters),
						client_filters or ALL,
						group
					)
				)

			return func

		return decorator
