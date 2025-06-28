import inspect

try:
	from pyrogram.sync import async_to_sync  #type: ignore
except ImportError:
	def async_to_sync(source, name):
		"""if we can't import it, we will just pass it.
		"""

from .clients import ClientManager


def wrap(source):
	for name in dir(source):
		method = getattr(source, name)

		if not name.startswith("_"):
			if inspect.iscoroutinefunction(method) or inspect.isasyncgenfunction(method):
				async_to_sync(source, name)

wrap(ClientManager)
