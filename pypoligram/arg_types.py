import asyncio
import inspect
from pathlib import Path
from typing import Optional, TypedDict, Union

from pyrogram import Client, enums, raw
from pyrogram.connection import Connection
from pyrogram.connection.transport import TCP
from pyrogram.storage import Storage


class ClientArgTypes(TypedDict, total=False):
	api_id: Union[int, str, None]
	api_hash: Union[str, None]
	app_version: str
	device_model: str
	system_version: str
	lang_pack: str
	lang_code: str
	system_lang_code: str
	ipv6: Union[bool, None]
	proxy: Union[dict, None]
	test_mode: Union[bool, None]
	bot_token: Union[str, None]
	session_string: Union[str, None]
	in_memory: Union[bool, None]
	phone_number: Union[str, None]
	phone_code: Union[str, None]
	password: Union[str, None]
	workers: int
	workdir: Union[str, Path]
	plugins: Union[dict, None]
	parse_mode: "enums.ParseMode"
	no_updates: Union[bool, None]
	skip_updates: Union[bool, None]
	takeout: Union[bool, None]
	sleep_threshold: int
	hide_password: Union[bool, None]
	max_concurrent_transmissions: int
	max_message_cache_size: int
	max_topic_cache_size: int
	storage_engine: Union[Storage, None]
	client_platform: "enums.ClientPlatform"
	fetch_replies: Union[bool, None]
	fetch_topics: Union[bool, None]
	fetch_stories: Union[bool, None]
	init_connection_params: Optional["raw.base.JSONValue"]
	connection_factory: type[Connection]
	protocol_factory: type[TCP]
	loop: Union[asyncio.AbstractEventLoop, None]

__fullargspec = inspect.getfullargspec(Client)
if __fullargspec.defaults is None:
    # pyromod patched the client and we cannot access it
    __fullargspec = inspect.getfullargspec(Client.old__init__)
__diff: int = len(__fullargspec.args) - len(__fullargspec.defaults)
default_args: ClientArgTypes = {arg[0]: arg[1] for arg in zip(__fullargspec.args[__diff:], __fullargspec.defaults)}
