from typing import Callable, Union, Optional

import pyrogram
from pyrogram.filters import Filter

import pypoligram
from pypoligram.filters import ALL, Filter as PFilter


class OnEditedMessage:
	def on_edited_message(
		self: Union["OnEditedMessage", PFilter, Filter, None] = None,
		client_filters: Union[PFilter, Filter, None] = None,
		filters: Optional[Filter] = None,
		group: int = 0
	) -> Callable:
		"""Decorator for handling edited messages.
  
		This does the same thing as :meth:`~pypoligram.ClientManager.add_handler` using the
		:obj:`~pyrogram.handlers.EditedMessageHandler`.
  
		Parameters:
			client_filters (:obj:`~pypoligram.filters`, *optional*):
				Pass one or more filters to allow only a subset of clients to be passed
				in your function.

			filters (:obj:`~pyrogram.filters`, *optional*):
				Pass one or more filters to allow only a subset of edited messages to be passed
				in your function.
	
			group (``int``, *optional*):
				The group identifier, defaults to 0.
		"""

		def decorator(func: Callable) -> Callable:
			nonlocal self, client_filters, filters, group
			if isinstance(self, pypoligram.ClientManager):
				self.add_handler(client_filters or ALL, pyrogram.handlers.EditedMessageHandler(func, filters), group)
			elif isinstance(self, Union[PFilter, Filter]) or self is None:
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
						client_filters or ALL,
						pyrogram.handlers.EditedMessageHandler(func, filters),
						group
					)
				)

			return func

		return decorator