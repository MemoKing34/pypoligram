#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

pyrogram_dec = Path(".venv") / 'lib' / f'python3.{sys.version_info.minor}' / 'site-packages' / 'pyrogram' / 'methods' / 'decorators'
if '--release' in sys.argv:
    pypoligram_dec = Path("pypoligram") / 'decorators'
else:
    pypoligram_dec = Path("downloads") / 'decorators'
    pypoligram_dec.mkdir(parents=True, exist_ok=True)
initpy_path = pypoligram_dec / '__init__.py'

CLIENT_FILTERS_DOCLINES = [
    "\t\t\tclient_filters (:obj:`~pypoligram.filters`, *optional*):\n",
    "\t\t\t\tPass one or more filters to allow only a subset of clients to be passed\n",
    "\t\t\t\tin your function.\n",
    "\n"
]

IMPORT_LINES = [
    "\n",
    "import pypoligram\n",
    "from pypoligram.filters import ALL\n",
    "from pypoligram.filters import Filter as PFilter\n",
]

SWAP_CODE_LINES = {
    True: [
        "\t\t\t\tif isinstance(self, PFilter) or self is None:\n",
        "\t\t\t\t\tclient_filters, self = self, client_filters\n",
    ],
    False: [
        "\t\t\t\tif isinstance(self, PFilter):\n",
        "\t\t\t\t\tclient_filters, self = self, client_filters\n",
        "\t\t\t\tif isinstance(self, Filter):\n",
        "\t\t\t\t\tfilters, self = self, filters\n",
        "\t\t\t\tif isinstance(self, int):\n",
        "\t\t\t\t\tgroup = self or 0\n",
    ]
}

INITPY_FILE = "{}\n\nclass Decorators(\n{}):\n\tpass\n"
INITPY_CONTENT = {
    False: "from .{} import {}\n",
    True: "\t{},\n"
}

names: list[tuple[str, str]] = []
for dec_path in pyrogram_dec.glob('on_*.py'):
    poli_dec_path = pypoligram_dec / dec_path.name
    code_lines: list[str] = []
    delete_lines: int = 0
    class_name: str | None = None
    handler_name: str | None = None
    only_self: bool = False
    imported: bool = False
    with dec_path.open() as dec_file:
        for line in dec_file:
            if line.startswith('#'):
                delete_lines = 1
                continue
            if delete_lines:
                delete_lines -= 1
                continue

            if 'from typing import TYPE_CHECKING\n' == line:
                line = 'from typing import TYPE_CHECKING, Optional\n'
            if 'from typing import TYPE_CHECKING, Optional\n' == line:
                line = 'from typing import TYPE_CHECKING, Optional, Union\n'
            if 'from .handler_type import HandlerType' == line.strip():
                line = line.replace('.handler_type', 'pyrogram.methods.decorators.handler_type')

            if line.startswith('class On'):
                class_name = line.removeprefix('class ').removesuffix(':\n').strip()
                _index = code_lines.index('import pyrogram\n')
                if 'from pyrogram.filters import Filter\n' != code_lines[_index+1] and (not imported):
                    for _i, _line in enumerate(IMPORT_LINES, _index+1):
                        code_lines.insert(_i, _line)
                    imported = True
                names.append((poli_dec_path.stem, class_name))

            if line.strip().startswith('def on_') and 'self' in line:
                line = line.replace(f'{class_name} | None', f'{class_name} | PFilter | None = None, client_filters: PFilter | None')
                only_self = True

            if line.strip().startswith('self'):
                line = line.replace('Filter', 'PFilter | Filter')

            if line.strip().startswith('filters') and line.endswith(',\n'):
                if 'filters=filters,' == line.strip():
                    code_lines.append("\t\t\t\t\tclient_filters=client_filters,\n")
                else:
                    code_lines.append("\t\tclient_filters: PFilter | Filter | None = None,\n")

            if 'pyrogram.Client.add_handler' in line:
                line = line.replace('pyrogram.Client.add_handler', 'pypoligram.ClientManager.add_handler')

            if (_line := line.strip()).startswith(':obj:`~pyrogram.handlers.') and _line.endswith('`.'):
                handler_name = _line.removeprefix(':obj:`~pyrogram.handlers.').removesuffix('`.')

            if line.strip().startswith('filters') and line.endswith(':\n'):
                code_lines.extend(CLIENT_FILTERS_DOCLINES)
            if '"""' == line.strip():
                try:
                    _index = code_lines.index('\t\tParameters:\n')
                except ValueError:
                    code_lines.extend(['\n', '\t\tParameters:\n'] + CLIENT_FILTERS_DOCLINES[:-1])

            if '~pyrogram.handlers' in line:
                delete_lines = 2

            if 'if isinstance(self, pyrogram.Client):' == line.strip():
                line = line.replace('pyrogram.Client', 'pypoligram.ClientManager')

            if f'(pyrogram.handlers.{handler_name}(func))' in line:
                line = line.replace(f'(pyrogram.handlers.{handler_name}(func))', f'(pyrogram.handlers.{handler_name}(func), client_filters or ALL)')
            if f'pyrogram.handlers.{handler_name}(func, filters), group' in line:
                line = line.replace(f'pyrogram.handlers.{handler_name}(func, filters), group', f'pyrogram.handlers.{handler_name}(func, filters), client_filters or ALL, group')
            if f'pyrogram.handlers.{handler_name}(func, exceptions, filters), group' in line:
                line = line.replace(f'pyrogram.handlers.{handler_name}(func, exceptions, filters), group', f'pyrogram.handlers.{handler_name}(func, exceptions, filters), client_filters or ALL, group')

            if 'unbound_arguments(self, filters=filters, group=group)' in line:
                line = line.replace('unbound_arguments(self, filters=filters, group=group)', 'unbound_arguments(self, client_filters=client_filters, filters=filters, group=group)')
            
            if line.strip().startswith('func.handlers.append') and line.endswith('))\n') and only_self:
                line = f'\t\t\t\tfunc.handlers.append((pyrogram.handlers.{handler_name}(func), client_filters or ALL, 0))\n'

            if f'(pyrogram.handlers.{handler_name}(func, arguments.filters), arguments.group)' in line:
                line = line.replace(f'(pyrogram.handlers.{handler_name}(func, arguments.filters), arguments.group)', f'(pyrogram.handlers.{handler_name}(func, arguments.filters), arguments.client_filters or ALL, arguments.group)')

            # *************** GOLDEN LINE ***************
            code_lines.append(line.replace('    ', '\t'))
            # *************** GOLDEN LINE ***************

            if 'from pyrogram.filters import Filter\n' == line and (not imported):
                code_lines.extend(IMPORT_LINES)
                imported = True

            if 'arguments.group,' == line.strip():
                code_lines.insert(-1, '\t\t\t\t\t\targuments.client_filters or ALL,\n')


    with poli_dec_path.open('w') as poli_dec_file:
        #poli_dec_file.writelines(code_lines)
        for code_line in code_lines:
            _ = poli_dec_file.write(code_line.expandtabs(4))


lines: dict[bool, list[str]] = {False: [], True: []}
for module_name, ClassName in names:
    lines[False].append(INITPY_CONTENT[False].format(module_name, ClassName))
    lines[True].append(INITPY_CONTENT[True].format(ClassName))
_ = initpy_path.write_text(
    INITPY_FILE.format(''.join(lines[False]), ''.join(lines[True]).expandtabs(4))
)
