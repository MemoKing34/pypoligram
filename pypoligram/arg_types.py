import asyncio
from pathlib import Path
from typing import Optional, Type, TypedDict, Union
import inspect

from pyrogram import Client, enums, raw
from pyrogram.storage import Storage
from pyrogram.connection import Connection
from pyrogram.connection.transport import TCP


class ClientArgTypes(TypedDict, total=False):
	api_id: Optional[Union[int, str]]
	api_hash: Optional[str]
	app_version: str
	device_model: str
	system_version: str
	lang_pack: str
	lang_code: str
	system_lang_code: str
	ipv6: Optional[bool]
	proxy: Optional[dict]
	test_mode: Optional[bool]
	bot_token: Optional[str]
	session_string: Optional[str]
	in_memory: Optional[bool]
	phone_number: Optional[str]
	phone_code: Optional[str]
	password: Optional[str]
	workers: int
	workdir: Union[str, Path]
	plugins: Optional[dict]
	parse_mode: "enums.ParseMode"
	no_updates: Optional[bool]
	skip_updates: Optional[bool]
	takeout: Optional[bool]
	sleep_threshold: int
	hide_password: Optional[bool]
	max_concurrent_transmissions: int
	max_message_cache_size: int
	max_topic_cache_size: int
	storage_engine: Optional[Storage]
	client_platform: "enums.ClientPlatform"
	fetch_replies: Optional[bool]
	fetch_topics: Optional[bool]
	fetch_stories: Optional[bool]
	init_connection_params: Optional["raw.base.JSONValue"]
	connection_factory: Type[Connection]
	protocol_factory: Type[TCP]
	loop: Optional[asyncio.AbstractEventLoop]

__fullargspec = inspect.getfullargspec(Client)
__diff: int = len(__fullargspec.args) - len(__fullargspec.defaults)
default_args: ClientArgTypes = {arg[0]: arg[1] for arg in zip(__fullargspec.args[__diff:], __fullargspec.defaults)}
