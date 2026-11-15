import asyncio
import contextlib
import inspect
import logging
from typing import Any

import pyrogram
from pyrogram import dispatcher
from pyrogram.handlers import RawUpdateHandler, Handler, ErrorHandler

import pypoligram

log = logging.getLogger(__name__)

class Dispatcher(dispatcher.Dispatcher):
	def __init__(self, client: "pyrogram.Client", clients: "pypoligram.ClientManager") -> None:
		self.clients = clients
		super().__init__(client)

	async def handler_worker(self) -> None:
		while True:
			packet = await self.updates_queue.get()

			if packet is None:
				break

			try:
				update, users, chats = packet
				parser = self.update_parsers.get(type(update), None)

				parsed_update, handler_type = (
					await parser(update, users, chats) if parser is not None else (None, type(None))
				)

				for group in self.groups.values():
					for handler in group:
						if isinstance(handler, ErrorHandler):
							continue

						args: tuple[Any, ...] | None = None

						if isinstance(handler, handler_type):
							try:
								if await handler.check(self.client, parsed_update):
									args = (parsed_update,)
							except Exception as e:
								log.exception(e)
								continue

						elif isinstance(handler, RawUpdateHandler):
							try:
								if await handler.check(self.client, update):
									args = (update, users, chats)
							except Exception as e:
								log.exception(e)
								continue

						if args is None:
							continue

						try:
							if inspect.iscoroutinefunction(handler.callback):
								await handler.callback(self.clients, self.client, *args)
							else:
								await asyncio.get_running_loop().run_in_executor(
									self.client.executor,
									handler.callback,
									self.clients,
									self.client,
									*args,
								)
						except pyrogram.StopPropagation:
							raise
						except pyrogram.ContinuePropagation:
							continue
						except Exception as exc:
							await self.handle_update_handler_exception(
								exc,
								handler,
								update,
								users,
								chats,
							)

						break
			except pyrogram.StopPropagation:
				pass
			except Exception as e:
				log.exception(e)

	async def handle_update_handler_exception(
		self,
		exc: Exception,
		update_handler: Handler[Any],
		update: pyrogram.raw.base.Update,
		users: dict[int, pyrogram.raw.base.User],
		chats: dict[int, pyrogram.raw.base.Chat],
	) -> None:
		handled = False
		try:
			for group in self.groups.values():
				for handler in group:
					if not isinstance(handler, ErrorHandler):
						continue

					if not isinstance(exc, handler.exceptions):
						continue

					try:
						if inspect.iscoroutinefunction(handler.callback):
							await handler.callback(
								self.clients, self.client, exc, update_handler, update, users, chats
							)
						else:
							await asyncio.get_running_loop().run_in_executor(
								self.client.executor,
								handler.callback,
								self.clients,
								self.client,
								exc,
								update_handler,
								update,
								users,
								chats,
							)
					except pyrogram.StopPropagation:
						handled = True
						raise
					except pyrogram.ContinuePropagation:
						handled = True
						continue
					except Exception:
						log.exception("Error handler raised an exception:")
					else:
						handled = True

					break
		except pyrogram.StopPropagation:
			pass
		finally:
			if not handled:
				log.error(
					f"Unexpected exception raised in {type(update_handler).__name__}:",
					exc_info=(type(exc), exc, exc.__traceback__),
				)
