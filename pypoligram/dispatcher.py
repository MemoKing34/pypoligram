import inspect
import logging

import pyrogram
from pyrogram import dispatcher
from pyrogram.handlers import RawUpdateHandler

import pypoligram

log = logging.getLogger(__name__)

class Dispatcher(dispatcher.Dispatcher):
	def __init__(self, client: "pyrogram.Client", clients: "pypoligram.ClientManager") -> None:
		self.clients = clients
		super().__init__(client)

	async def handler_worker(self, lock):
		while True:
			packet = await self.updates_queue.get()

			if packet is None:
				break

			try:
				update, users, chats = packet
				parser = self.update_parsers.get(type(update), None)

				parsed_update, handler_type = (
					await parser(update, users, chats)
					if parser is not None
					else (None, type(None))
				)

				async with lock:
					for group in self.groups.values():
						for handler in group:
							args = None

							if isinstance(handler, handler_type):
								try:
									if await handler.check(self.client, parsed_update):
										args = (parsed_update,)
								except Exception as e:
									log.exception(e)
									continue

							elif isinstance(handler, RawUpdateHandler):
								args = (update, users, chats)

							if args is None:
								continue

							try:
								if inspect.iscoroutinefunction(handler.callback):
									await handler.callback(self.clients, self.client, *args)
								else:
									await self.loop.run_in_executor(
										self.client.executor,
										handler.callback,
										self.clients,
										self.client,
										*args
									)
							except pyrogram.StopPropagation:
								raise
							except pyrogram.ContinuePropagation:
								continue
							except Exception as e:
								log.exception(e)

							break
			except pyrogram.StopPropagation:
				pass
			except Exception as e:
				log.exception(e)
