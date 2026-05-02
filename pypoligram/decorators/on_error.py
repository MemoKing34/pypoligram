from typing import Callable, Optional, Sequence, Union

import pyrogram
from pyrogram.filters import Filter

import pypoligram
from pypoligram.filters import ALL
from pypoligram.filters import Filter as PFilter


class OnError:
	def on_error(
		self: Optional[Union["OnError", PFilter, Filter]] = None,
		exceptions: Optional[Union[Exception, Sequence[Exception]]] = None,
		client_filters: Optional[Union[PFilter, Filter]] = None,
		filters: Optional[Filter] = None,
		group: int = 0,
	) -> Callable:
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
				Pass one or more filters to allow only a subset of messages to be passed
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
				self.add_handler(pyrogram.handlers.ErrorHandler(func, filters), client_filters or ALL, group)
			else:
				if not hasattr(func, "handlers"):
					func.handlers = []
				if isinstance(self, PFilter):
					client_filters, self = self, client_filters
				if isinstance(self, Filter):
					filters, self = self, filters
				if isinstance(self, int):
					group = self or 0

				func.handlers.append(
					(pyrogram.handlers.ErrorHandler(func, exceptions, filters), group)
				)

			return func

		return decorator
