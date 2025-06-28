from typing import Callable, Optional, Union

import pyrogram

import pypoligram
from pypoligram.filters import ALL, Filter as PFilter


class OnDisconnect:
	def on_disconnect(self: Union["OnDisconnect", PFilter, None] = None, client_filters: Optional[PFilter] = None):
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
				self.add_handler(client_filters or ALL, pyrogram.handlers.DisconnectHandler(func))
			else:
				if not hasattr(func, "handlers"):
					func.handlers = []
				if isinstance(self, PFilter) or self is None:
					client_filters, self = self, client_filters
				
				func.handlers.append((client_filters or ALL, pyrogram.handlers.DisconnectHandler(func), 0))
			
			return func
		
		return decorator
