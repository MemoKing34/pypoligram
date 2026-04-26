from pathlib import Path
import re
import builtins

client_path = Path(".venv") / 'lib' / 'python3.14' / 'site-packages' / 'pyrogram' / 'client.py'
argtypes_path = Path("pypoligram") / 'arg_types.py'

FILE_TEMPLATE = """import asyncio
import inspect
from pathlib import Path
from typing import Optional, Type, TypedDict, Union

from pyrogram import Client, enums, raw
from pyrogram.connection import Connection
from pyrogram.connection.transport import TCP
from pyrogram.storage import Storage
from pyrogram.types import LinkPreviewOptions


class ClientArgTypes(TypedDict, total=False):
{0}
__fullargspec = inspect.getfullargspec(Client)
if __fullargspec.defaults is None:
    # pyromod patched the client and we cannot access it
    __fullargspec = inspect.getfullargspec(Client.old__init__)
__diff: int = len(__fullargspec.args) - len(__fullargspec.defaults)
{1}
"""

EOF_ = "default_args: ClientArgTypes = {arg[0]: arg[1] for arg in zip(__fullargspec.args[__diff:], __fullargspec.defaults)}"
ARG_TEMPLATE = "\t{0}: {1}\n"

builtins_list = dir(builtins)

# region find_init
#client_type_list: list[str] = []
client_type_dict: dict[str, str] = {}
with client_path.open() as cfile:
    should_print = False
    j = 0
    for i, line in enumerate(cfile, start=1):
        if line.strip().startswith("def __init__("):
            should_print = True
        if line.strip() == '):':
            should_print = False
            break
        if should_print:
            #print(i, line, sep="|", end='')
            j += 1
            if j < 4:
                continue
            #client_type_list.append(line)
            key, value, *_ = re.split(r'[:=]', line)
            client_type_dict[key.strip()] = value.strip().strip(',')
#print(client_type_dict)
# endregion


# region find_argtype
argtypes_dict: dict[str, str] = {}
with argtypes_path.open('r+') as afile:
    should_print = False
    for i, line in enumerate(afile, start=1):
        if line.strip().startswith("class"):
            should_print = True
            continue
        if line.strip().startswith('__fullargspec'):
            should_print = False
            break
        if should_print and line.strip():
            #print(i, line, sep="|", end='')
            key, value = line.split(':')
            argtypes_dict[key.strip()] = value.strip()
#print(argtypes_dict)
# endregion

lines = []
for key in client_type_dict:
    #print(f"{key=}\n{client_type_dict[key]=}\n{argtypes_dict.get(key)=}")
    lines.append(ARG_TEMPLATE.format(key, client_type_dict[key]))


output = FILE_TEMPLATE.format(''.join(lines), EOF_)
print(output)
argtypes_path.write_text(output)
