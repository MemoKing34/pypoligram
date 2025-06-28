import inspect
from typing import Callable, List, Union

import pyrogram
from pyrogram.filters import Filter, create

import pypoligram


class Filter:
	def __call__(self, clients: "pypoligram.ClientManager", client: "pyrogram.Client"):
		raise NotImplementedError

	def __invert__(self):
		return InvertFilter(self)

	def __and__(self, other):
		return AndFilter(self, other)

	def __or__(self, other):
		return OrFilter(self, other)

	def check(self, clients: "pypoligram.ClientManager", client: "pyrogram.Client"):
		return self(clients, client)


class InvertFilter(Filter):
	def __init__(self, base):
		self.base = base

	def __call__(self, clients: "pypoligram.ClientManager", client: "pyrogram.Client"):
		return not self.base(clients, client)


class AndFilter(Filter):
	def __init__(self, base, other):
		self.base = base
		self.other = other

	def __call__(self, clients: "pypoligram.ClientManager", client: "pyrogram.Client"):
		if not self.base(clients, client):
			return False
		return self.other(clients, client)


class OrFilter(Filter):
	def __init__(self, base, other):
		self.base = base
		self.other = other

	def __call__(self, clients: "pypoligram.ClientManager", client: "pyrogram.Client"):
		if self.base(clients, client):
			return True
		return self.other(clients, client)


CUSTOM_FILTER_NAME = "CustomFilter"


def create(func: Callable, name: str = None, **kwargs) -> Filter:
	"""Easy way to create a custom filter
 
	Custom filters give you extra flexibility to filter clients based on your own logic.
 
	Parameters:	
		func (``Callable``):
			A function that takes three positional arguments *(filter, manager, client)* and returns a boolean: True if the
			client should be registered the handler, False otherwise.
			The *filter* argument refers to filter itself and can be used to access keyword arguments (read below).
			The *manager* argument refers to the :obj:`pypoligram.ClientManager` and can be used to access the clients.
			The *client* argument refers to the :obj:`pyrogram.Client` and can be used to access the client.
   
		name (``str``, *optional*):
			The name of the filter. If not provided, the name of the function will be used.
			Defaults to "CustomFilter".
   
		**kwargs (``dict``, *optional*):
			Any additional keyword arguments that you want to pass to the filter.
			These will be available in the *filter* argument of the function.
	"""
	return type(
		name or func.__name__ or CUSTOM_FILTER_NAME,
		(Filter,),
		{"__call__": func, **kwargs}
	)()


# region all_filter
def all_filter(_, __, ___):
	return True


ALL = create(all_filter, "ALL")
"""Filter all clients."""


# endregion

# region user_filter
def user_filter(_, __, client: "pyrogram.Client"):
	return not bool(client.bot_token)


USER = create(user_filter, "USER")
"""Filter all users (non-bot clients).
This filter detects if the client is a user or not by checking the *bot_token* attribute."""


# endregion

# region bot_filter
def bot_filter(_, __, client: "pyrogram.Client"):
	return bool(client.bot_token)


BOT = create(bot_filter, "BOT")
"""Filter all bots (bot clients).
This filter detects if the client is a bot or not by checking the *bot_token* attribute."""


# endregion

# region client_filter
class client(Filter, set):
	"""Filter clients by its *name* attribute.
 
	Parameters:
		clients (``str`` | ``list``):
			A string or a list of strings containing the names of the clients to filter.
   	"""
    
	def __init__(self, clients: Union[str, List[str]]):
		clients = [] if clients is None else clients if isinstance(clients, list) else [clients]
		super().__init__(clients)

	def __call__(self, _, client: "pyrogram.Client"):
		return client.name in self

# endregion
