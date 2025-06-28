from collections.abc import Callable
from typing import Union

import pyrogram
from pyrogram.filters import Filter

import pypoligram
from pypoligram.filters import ALL
from pypoligram.filters import Filter as PFilter


class OnDeletedMessages:
	def on_deleted_messages(
		self: Union["OnDeletedMessages", PFilter, Filter, None] = None,
		client_filters: PFilter | Filter | None = None,
		filters: Filter | None = None,
		group: int = 0
	) -> Callable:
		"""Decorator for handling deleted messages.
  
		This does the same thing as :meth:`~pypoligram.ClientManager.add_handler` using the
		:obj:`~pyrogram.handlers.DeletedMessagesHandler`.
  
		Parameters:
			client_filters (:obj:`~pypoligram.filters`, *optional*):
				Pass one or more filters to allow only a subset of clients to be passed
				in your function.

			filters (:obj:`~pyrogram.filters`, *optional*):
				Pass one or more filters to allow only a subset of deleted messages to be passed
				in your function.
	
			group (``int``, *optional*):
				The group identifier, defaults to 0.
		"""

		def decorator(func: Callable) -> Callable:
			nonlocal self, client_filters, filters, group
			if isinstance(self, pypoligram.ClientManager):
				self.add_handler(pyrogram.handlers.DeletedMessagesHandler(func, filters), client_filters or ALL, group)
			elif isinstance(self, Union[PFilter, Filter]) or self is None:
				if not hasattr(func, "handlers"):
					func.handlers = []
				if isinstance(self, PFilter):
					client_filters, self = self, client_filters
				if isinstance(self, Filter):
					filters, self = self, filters
				if isinstance(self, int) or self is None:
					group = self or 0

				func.handlers.append(
					(
						pyrogram.handlers.DeletedMessagesHandler(func, filters),
						client_filters or ALL,
						group
					)
				)

			return func

		return decorator
