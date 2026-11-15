from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from typing import Dict, Optional, Type, TypedDict, Union

from pyrogram import Client, enums, raw
from pyrogram.connection import Connection, Proxy
from pyrogram.connection.proxy import ProxyDict
from pyrogram.connection.transport import TCP
from pyrogram.storage import Storage
from pyrogram.types import LinkPreviewOptions
from pyrogram._typing import PathType


class ClientArgTypes(TypedDict, total=False):
    api_id: int | str | None
    api_hash: str | None
    app_version: str
    device_model: str
    system_version: str
    lang_pack: str
    lang_code: str
    system_lang_code: str
    ipv6: bool
    proxy: str | ProxyDict | Proxy | None
    test_mode: bool
    bot_token: str | None
    session_string: str | None
    in_memory: bool | None
    phone_number: str | None
    phone_code: str | None
    password: str | None
    workers: int
    workdir: PathType
    plugins: Dict | None
    parse_mode: enums.ParseMode
    no_updates: bool | None
    skip_updates: bool
    takeout: bool | None
    sleep_threshold: int
    hide_password: bool
    max_concurrent_transmissions: int
    max_message_cache_size: int
    max_topic_cache_size: int
    max_sticker_set_name_cache_size: int
    storage_engine: Storage | None
    client_platform: enums.ClientPlatform
    link_preview_options: LinkPreviewOptions | None
    fetch_replies: bool
    fetch_topics: bool
    fetch_stories: bool
    fetch_stickers: bool
    init_connection_params: Dict | raw.base.JSONValue | None
    connection_factory: type[Connection]
    protocol_factory: type[TCP]

__fullargspec = inspect.getfullargspec(Client)
if __fullargspec.defaults is None:
    # pyromod patched the client and we cannot access it
    __fullargspec = inspect.getfullargspec(Client.old__init__)
__diff: int = len(__fullargspec.args) - len(__fullargspec.defaults)
default_args: ClientArgTypes = {key: value for key, value in zip(__fullargspec.args[__diff:], __fullargspec.defaults)}
