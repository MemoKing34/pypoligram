import asyncio
import inspect
from pathlib import Path
from typing import Optional, TypedDict

from pyrogram import Client, enums, raw
from pyrogram.connection import Connection
from pyrogram.connection.transport import TCP
from pyrogram.storage import Storage


class ClientArgTypes(TypedDict, total=False):
	api_id: int | str | None
	api_hash: str | None
	app_version: str
	device_model: str
	system_version: str
	lang_pack: str
	lang_code: str
	system_lang_code: str
	ipv6: bool | None
	proxy: dict | None
	test_mode: bool | None
	bot_token: str | None
	session_string: str | None
	in_memory: bool | None
	phone_number: str | None
	phone_code: str | None
	password: str | None
	workers: int
	workdir: str | Path
	plugins: dict | None
	parse_mode: "enums.ParseMode"
	no_updates: bool | None
	skip_updates: bool | None
	takeout: bool | None
	sleep_threshold: int
	hide_password: bool | None
	max_concurrent_transmissions: int
	max_message_cache_size: int
	max_topic_cache_size: int
	storage_engine: Storage | None
	client_platform: "enums.ClientPlatform"
	fetch_replies: bool | None
	fetch_topics: bool | None
	fetch_stories: bool | None
	init_connection_params: Optional["raw.base.JSONValue"]
	connection_factory: type[Connection]
	protocol_factory: type[TCP]
	loop: asyncio.AbstractEventLoop | None

__fullargspec = inspect.getfullargspec(Client)
if __fullargspec.defaults is None:
    # pyromod patched the client and we cannot access it
    __fullargspec = inspect.getfullargspec(Client.old__init__)
__diff: int = len(__fullargspec.args) - len(__fullargspec.defaults)
default_args: ClientArgTypes = {arg[0]: arg[1] for arg in zip(__fullargspec.args[__diff:], __fullargspec.defaults, strict=False)}
