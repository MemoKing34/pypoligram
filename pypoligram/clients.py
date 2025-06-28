import asyncio
import inspect
import logging
from collections.abc import Iterable
from concurrent.futures.thread import ThreadPoolExecutor
from importlib import import_module
from pathlib import Path
from typing import Self

from pyrogram import Client
from pyrogram.dispatcher import Dispatcher
from pyrogram.handlers.handler import Handler

from .arg_types import ClientArgTypes, default_args
from .decorators import Decorators
from .dispatcher import Dispatcher as PDispatcher
from .filters import ALL as pALL
from .filters import Filter

log = logging.getLogger(__name__)


class ClientManager(Decorators):
	"""Pypoligram's Client Manager, the main class to manage multiple clients.
 
	Parameters:
		clients (``iterable``, *optional*):
			An iterable of :obj:`pyrogram.Client` instances to be added to the manager.
			You can pass a list, tuple, set, any other iterable or nothing at all.
			Defaults to ``None``.
	
		name (``str``, *optional*):
			The name of the manager. Defaults to ``"Clients"``.
	
		plugins (``dict``, *optional*):
			Smart Plugins settings as dict, e.g.: *dict(root="plugins")*.
			This plugin has some extra settings from normal pyrogram plugin settings in ordor to apply
			all the clients. For more information, please refer to the documentation.
   			Defaults to ``None``.
	
		dont_modify (``bool``, *optional*):
			If set to ``True``, the clients will not be modified. That means handler functions will not be
			get a manager argument and the dispatcher will not be replaced.
			You can use this option to add a client to the manager and then use it as a normal client.
   			Defaults to ``False``.
	
		kwargs (``dict``, *optional*):
			A dictionary with the kwargs to be passed to the all clients. If client has a different value for the
			argument, it will be ignored. You can use this option to set the same value for all clients.
   			Defaults to ``None``.
	"""

	def __init__(
     	self,
      	clients: Iterable[Client] = None, *,
       	name: str = "Clients",
		plugins: dict = None,
  		dont_modify: bool = False,
		kwargs: ClientArgTypes = None
  	):
		if kwargs is None:
			kwargs = {}
		self._clients: set[Client] = set()
		self.name = str(name)
		self.executor = ThreadPoolExecutor(4, thread_name_prefix="Clients")
		self.loop = asyncio.get_event_loop()
		self.plugins = plugins
		self._kwargs = kwargs.copy()
		self.dont_modify = dont_modify
		if clients is not None:
			[self.add_client(client) for client in clients]

	def add_client(self, client: Client, dont_add_kwargs: bool = False) -> Client:
		"""Add a client to the manager.
  
		Parameters:
			client (:obj:`pyrogram.Client`):
				The client to be added.
	
			dont_add_kwargs (``bool``, *optional*):
				Whether to add the kwargs to the client or not. Defaults to False.
    
		Returns:
			:obj:`~pyrogram.Client`: The added client itself.
   
		Example:
			.. code-block:: python
	
				from pyrogram import Client
				from pypoligram import ClientManager
	
				manager = ClientManager()
	
				client1 = Client("my_account1")
				client2 = Client("my_account2")
	
				manager.add_client(client1)
				manager.add_client(client2)
		"""
		self._clients.add(client)
		if not self.dont_modify:
			client.dispatcher = PDispatcher(client, self)
		client.plugins = None if self.plugins else client.plugins
		client._clients = self
		if not dont_add_kwargs:
			if self._kwargs:
				for name, value in self._kwargs.items():
					c_value = getattr(client, name)
					if c_value == default_args.get(name):  # type: ignore
						setattr(client, name, value)
		return client

	def discard_client(self, client: Client) -> Client:
		"""Remove a client from the manager.

		You have to give the exact same client instance you added to the manager to remove it. You can use the return 
		value of :metm:`~pypoligram.ClientManager.add_client` method, the client itself, and pass it directly. If the 
		client was not added to the manager, it will be ignored.
  
		Parameters:
			client (:obj:`pyrogram.Client`):
				The client to be removed.
    
		Returns:
			:obj:`~pyrogram.Client`: The removed client itself.
   
		Example:
			.. code-block:: python
	
				from pyrogram import Client
				from pypoligram import ClientManager
	
				manager = ClientManager()
	
				client1 = Client("my_account1")
				client2 = Client("my_account2")
	
				manager.add_client(client1)
				manager.add_client(client2)
	
				manager.discard_client(client1)
		"""
		if not self.dont_modify:
			client.dispatcher = Dispatcher(client)
		self._clients.discard(client)
		try:
			delattr(client, "_clients")
		except AttributeError:
			pass
		return client

	def add_handler(self, handler: Handler, filters: Filter = pALL, group: int = 0, **kwargs) -> tuple[Handler, int]:
		"""Register an update handler to multiple clients.
  
		You can use it just like :meth:`pyrogram.Client.add_handler` but it will register the handler to all clients in
  		the manager that pass :obj:`pypoligram.filters`.
    
		Parameters:
			handler (``Handler``):
				The handler to be registered.
	
			filters (:obj:`pypoligram.filters`, *optional*):
				The filter to filter the clients that will receive the handler, defaults to :obj:`pypoligram.filters.ALL`
	
			group (``int``, *optional*):
				The group identifier, defaults to 0.
    
		Returns:
			``tuple``: A tuple consisting of *(handler, group)*.
   
		Example:
			.. code-block:: python
	
				from pyrogram import Client
				from pyrogram.handlers import MessageHandler
				from pypoligram import ClientManager, filters as pfilters
	
				async def hello(client, message):
					print(message)
	
				manager = ClientManager([
					Client("my_account1"),
					Client("my_account2"),
				])
	
				manager.add_handler(pfilters.client("my_account1"), MessageHandler(hello), group=1)
	
				manager.run()
		"""
		names = []
		for client in self:
			if filters(self, client):
				client.add_handler(handler, group)
				names.append(client.name)
		if isinstance(kwargs.get("module_path"), str):
			log.info('[{}] [MULTILOAD] {}("{}") in group {} from "{}" added to {}'.format(
				self.name, type(handler).__name__, kwargs.get("name"), group, kwargs.get("module_path"), (", ".join(repr(name) for name in names[:-1])+f" and {names[-1]!r}") if len(names) > 1 else repr(names[0])))
		return handler, group

	def remove_handler(self, handler: Handler, group: int = 0, **kwargs) -> None:
		"""Remove a previously-registered update handler from multiple clients.
  
		Make sure to provide the right group where the handler was added in. You can use the return value of the
		:meth:`~pyrogram.Client.add_handler` method, a tuple of *(handler, group)*, and pass it directly.
  
		Parameters:
			handler (``Handler``):
				The handler to be removed.
  
			group (``int``, *optional*):
				The group identifier, defaults to 0.
    
		Example:
			.. code-block:: python
	
				from pyrogram import Client
				from pyrogram.handlers import MessageHandler
				from pypoligram import ClientManager
	
				async def hello(client, message):
					print(message)
	
				manager = ClientManager([
					Client("my_account1"),
					Client("my_account2"),
				])
	
				handler = manager.add_handler(pfilters.client("my_account1"), MessageHandler(hello))
	
				# Starred expression to unpack (handler, group)
				manager.remove_handler(*handler)
	
				manager.run()
		"""
		names = []
		for client in self:
			try:
				client.remove_handler(handler, group)
				names.append(client.name)
			except ValueError:
				pass
		if isinstance(kwargs.get("module_path"), str):
			log.info('[{}] [MULTIUNLOAD] {}("{}") in group {} from "{}" removed from {}'.format(
				self.name, type(handler).__name__, kwargs.get("name"), group, kwargs.get("module_path"), (", ".join(repr(name) for name in names[:-1])+f" and {names[-1]!r}") if len(names) > 1 else repr(names[0])))

	def load_plugins(self):
		if self.plugins:
			plugins = self.plugins.copy()

			for option in ["include", "exclude"]:
				if plugins.get(option, []):
					plugins[option] = [
						(i.split()[0], i.split()[1:] or None)
						for i in self.plugins[option]
					]
		else:
			return

		if plugins.get("enabled", True):
			root = plugins["root"]
			include = plugins.get("include", [])
			exclude = plugins.get("exclude", [])

			count = 0

			if not include:
				for path in sorted(Path(root.replace(".", "/")).rglob("*.py")):
					module_path = '.'.join(path.parent.parts + (path.stem,))
					module = import_module(module_path)

					for name in vars(module).keys():
						# noinspection PyBroadException
						try:
							for filters, handler, group in getattr(module, name).handlers:
								if isinstance(handler, Handler) and isinstance(group, int):
									self.add_handler(filters, handler, group, name=name, module_path=module_path)

									# log.info('[{}] [MULTILOAD] {}("{}") in group {} from "{}"'.format(
									#	self.name, type(handler).__name__, name, group, module_path))

									count += 1
						except Exception:
							pass
			else:
				for path, handlers in include:
					module_path = root + "." + path
					warn_non_existent_functions = True

					try:
						module = import_module(module_path)
					except ImportError:
						log.warning('[%s] [MULTILOAD] Ignoring non-existent module "%s"', self.name, module_path)
						continue

					if "__path__" in dir(module):
						log.warning('[%s] [MULTILOAD] Ignoring namespace "%s"', self.name, module_path)
						continue

					if handlers is None:
						handlers = vars(module).keys()
						warn_non_existent_functions = False

					for name in handlers:
						# noinspection PyBroadException
						try:
							for filters, handler, group in getattr(module, name).handlers:
								if isinstance(handler, Handler) and isinstance(group, int):
									self.add_handler(filters, handler, group, name=name, module_path=module_path)

									# log.info('[{}] [MULTILOAD] {}("{}") in group {} from "{}"'.format(
									#	self.name, type(handler).__name__, name, group, module_path))

									count += 1
						except Exception:
							if warn_non_existent_functions:
								log.warning(f'[{self.name}] [MULTILOAD] Ignoring non-existent function "{name}" from "{module_path}"')

			if exclude:
				for path, handlers in exclude:
					module_path = root + "." + path
					warn_non_existent_functions = True

					try:
						module = import_module(module_path)
					except ImportError:
						log.warning('[%s] [MULTIUNLOAD] Ignoring non-existent module "%s"', self.name, module_path)
						continue

					if "__path__" in dir(module):
						log.warning('[%s] [MULTIUNLOAD] Ignoring namespace "%s"', self.name, module_path)
						continue

					if handlers is None:
						handlers = vars(module).keys()
						warn_non_existent_functions = False

					for name in handlers:
						# noinspection PyBroadException
						try:
							for filters, handler, group in getattr(module, name).handlers:
								if isinstance(handler, Handler) and isinstance(group, int):
									self.remove_handler(filters, handler, group, name=name, module_path=module_path)

									# log.info('[{}] [MULTIUNLOAD] {}("{}") from group {} in "{}"'.format(
									#	self.name, type(handler).__name__, name, group, module_path))

									count -= 1
						except Exception:
							if warn_non_existent_functions:
								log.warning(f'[{self.name}] [MULTIUNLOAD] Ignoring non-existent function "{name}" from "{module_path}"')

			if count > 0:
				log.info('[{}] Successfully loaded {} plugin{} from "{}"'.format(
					self.name, count, "s" if count > 1 else "", root))
			else:
				log.warning('[%s] No plugin loaded from "%s"', self.name, root)

	def __iter__(self) -> Self:
		self.__iter: Iterable[Client] = iter(self._clients)
		return self

	async def __aiter__(self) -> Self:
		self.__aiter: Iterable[Client] = iter(self._clients)
		return self

	def __next__(self) -> Client:
		return next(self.__iter)

	async def __anext__(self) -> Client:
		try:
			return next(self.__aiter)
		except StopIteration:
			raise StopAsyncIteration

	def __enter__(self):
		return self.start()

	def __exit__(self, *args):
		try:
			self.stop()
		except ConnectionError:
			pass

	async def __aenter__(self):
		return await self.start()

	async def __aexit__(self, *args):
		try:
			await self.stop()
		except ConnectionError:
			pass

	async def start(self, sequential: bool = False) -> Self:
		"""Start all clients in the manager.
		
  		You can use it just like :meth:`pyrogram.Client.start` but it will start all clients in the manager.
    
		Parameters:
			sequential (``bool``, *optional*):
				Start the clients sequentially instead of concurrently.
				Defaults to False.
    
		Returns:
			:obj:`~pypoligram.ClientManager`: The started manager itself.
   
		Raises:
			ConnectionError: In case you try to start an already started client.
   
		Example:
			.. code-block:: python
   
				import asyncio
	
				from pyrogram import Client
				from pypoligram import ClientManager
	
				manager = ClientManager([
					Client("account1"),
					Client("account2"),
					Client("account3")
				])

	
				async def main():
					await manager.start()
					... # Invoke API methods
					await manager.stop()
	
				asyncio.run(main())
		"""
		self.load_plugins()
		if sequential:
			for client in self:
				await client.start()
			return self
		await asyncio.gather(*[client.start() for client in self])
		return self

	async def stop(self, sequential: bool = False, block: bool = True) -> Self:
		"""Stop all clients in the manager.
		
  		You can use it just like :meth:`pyrogram.Client.stop` but it will stop all clients in the manager.
    
		Parameters:
			sequential (``bool``, *optional*):
				Stop the clients sequentially instead of concurrently.
				Defaults to False.
	
			block (``bool``, *optional*):
				Blocks the code execution until all the clients has been stopped. It is useful with ``block=False`` in
				case you want to stop the own client *within* a handler in order not to cause a deadlock. 
				Defaults to True.
    
		Returns:
			:obj:`~pypoligram.ClientManager`: The stopped manager itself.
   
		Raises:
			ConnectionError: In case you try to stop an already stopped client.
   
		Example:
			.. code-block:: python
	
				import asyncio
	
				from pyrogram import Client
				from pypoligram import ClientManager
	
				manager = ClientManager([
					Client("account1"),
					Client("account2"),
					Client("account3")
				])
	
				async def main():
					await manager.start()
					... # Invoke API methods
					await manager.stop()
     
				asyncio.run(main())
		"""
		async def do_it():
			if sequential:
				for client in self:
					await client.stop()
				return self
			await asyncio.gather(*[client.stop() for client in self])
		if block:
			await do_it()
		else:
			self.loop.create_task(do_it())

		return self

	async def restart(self, sequential: bool = False, block: bool = True) -> Self:
		"""Restart all clients in the manager.
		
  		This method calls :meth:`pyrogram.Client.restart` for every client in the manager.
    
		Parameters:
			sequential (``bool``, *optional*):
				Restart the clients sequentially instead of concurrently.
				Defaults to False.
    
			block (``bool``, *optional*):
				Blocks the code execution until all the clients has been restarted. It is useful with ``block=False`` in
				case you want to restart the own client *within* a handler in order not to cause a deadlock. 
				Defaults to True.
    
		Returns:
			:obj:`~pypoligram.ClientManager`: The restarted manager itself.
   
		Raises:
			ConnectionError: In case you try to restart a stopped client.
   
		Example:
			.. code-block:: python
	
				import asyncio
	
				from pyrogram import Client
				from pypoligram import ClientManager
	
				manager = ClientManager([
					Client("account1"),
					Client("account2"),
					Client("account3")
				])
	
				async def main():
					await manager.start()
					... # Invoke API methods
					await manager.restart()
					... # Invoke other API methods
					await manager.stop()
     
				asyncio.run(main())
		"""
		async def do_it():
			if sequential:
				for client in self:
					await client.restart()
				return self
			await asyncio.gather(*[client.restart() for client in self])

		if block:
			await do_it()
		else:
			self.loop.create_task(do_it())

		return self

	async def restart2(self, sequential: bool = False, block: bool = True) -> Self:
		"""Restart all clients in the manager.
		
  		This method will call :meth:`pypoligram.ClientManager.stop` and then :meth:`pypoligram.ClientManager.start` in a row instead of
		calling :meth:`pyrogram.Client.restart` for every client in the manager.
  
		Parameters:
			sequential (``bool``, *optional*):
				Restart the clients sequentially instead of concurrently.
				Defaults to False.
	
			block (``bool``, *optional*):
				Blocks the code execution until all the clients has been restarted. It is useful with ``block=False`` in
				case you want to restart the own client *within* a handler in order not to cause a deadlock. 
				Defaults to True.
    
		Returns:
			:obj:`~pypoligram.ClientManager`: The restarted manager itself.
   
		Raises:
			ConnectionError: In case you try to restart a stopped client.
   
		Example:
			.. code-block:: python
	
				import asyncio
	
				from pyrogram import Client
				from pypoligram import ClientManager
	
				manager = ClientManager([
					Client("account1"),
					Client("account2"),
					Client("account3")
				])
	
				async def main():
					await manager.start()
					... # Invoke API methods
					await manager.restart()
					... # Invoke other API methods
					await manager.stop()
     
				asyncio.run(main())
		"""
		async def do_it():
			await self.stop(sequential=sequential)
			await self.start(sequential=sequential)

		if block:
			await do_it()
		else:
			self.loop.create_task(do_it())

		return self

	def run(self, coroutine=None, /, *, sequential: bool = False) -> None:
		"""Start the manager, idle the main script and finally stop the manager.
  
		When calling this method without any argument it acts as a convenience method that calls
		:meth:`~pypoligram.ClientManager.start`, :meth:`~pyrogram.idle` and :meth:`~pypoligram.ClientManager.stop` in sequence.
		It makes running a single client less verbose.
  
		In case a coroutine is passed, runs the coroutine until it's completed and doesn't do any client
        operation. This is almost the same as :py:obj:`asyncio.run` except for the fact that PyPoligram's ``run`` uses the
        current event loop instead of a new one.
        
		Parameters:
			coroutine (``coroutine``, *optional*):
				The coroutine to run. If not provided, the manager will be started and idled.
	
			sequential (``bool``, *optional*):
				Start the clients sequentially instead of concurrently.
				Defaults to False.
    
		Raises:
			ConnectionError: In case you try to run an already started client.
   
		Example:
			.. code-block:: python
	
				from pyrogram import Client
				from pypoligram import ClientManager
	
				manager = ClientManager([
					Client("account1"),
					Client("account2"),
					Client("account3")
				])
				... # Set handlers up
				manager.run()
	
			.. code-block:: python
	
				from pyrogram import Client
				from pypoligram import ClientManager
				
				manager = ClientManager([
					Client("account1"),
					Client("account2"),
					Client("account3")
				])
    
				async def main():
					async with manager:
						... # Do something with the clients
      
      
				manager.run(main())
		"""
		loop = asyncio.get_event_loop()
		run = loop.run_until_complete
		from pyrogram.methods.utilities.idle import idle

		if coroutine is not None:
			run(coroutine)
		elif inspect.iscoroutinefunction(self.start):
			run(self.start(sequential))
			run(idle())
			run(self.stop(sequential=sequential))
		else:
			self.start(sequential)
			run(idle())
			self.stop(sequential=sequential)
