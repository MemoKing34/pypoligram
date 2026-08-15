#!/usr/bin/env python3

from pathlib import Path

pyrogram_dec = Path(".venv") / 'lib' / 'python3.13' / 'site-packages' / 'pyrogram' / 'methods' / 'decorators'
pypoligram_dec = Path("pypoligram") / 'decorators'
pypoligram_dec = Path("downloads") / 'decorators'; pypoligram_dec.mkdir(parents=True, exist_ok=True)
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
    poli_dec_path = pypoligram_dec/dec_path.name
    if pypoligram_dec.parent.name == 'pypoligram' and poli_dec_path.exists():
        continue
    code_lines: list[str] = []
    delete_lines: int = 0
    class_name: str = None   # pyright: ignore[reportAssignmentType]
    handler_name: str = None # pyright: ignore[reportAssignmentType]
    only_self: bool = False
    with dec_path.open() as dec_file:
        for line in dec_file:
            if line.startswith('#'):
                delete_lines = 1
                continue
            if delete_lines:
                delete_lines -= 1
                continue

            if 'from typing import Callable\n' == line:
                line = 'from typing import Callable, Optional\n'
            if 'from typing import Callable, Optional\n' == line:
                line = 'from typing import Callable, Optional, Union\n'

            if line.startswith('class On'):
                class_name = line.lstrip('class ').rstrip(':\n')
                _index = code_lines.index('import pyrogram\n')
                if 'from pyrogram.filters import Filter\n' != code_lines[_index+1]:
                    for _i, _line in enumerate(IMPORT_LINES, _index+1):
                        code_lines.insert(_i, _line)
                names.append((poli_dec_path.stem, class_name))

            if line.strip().startswith('def on_') and 'self' in line:
                line = line.replace(f'Optional["{class_name}"]', f'Optional[Union["{class_name}", PFilter]] = None, client_filters: Optional[PFilter]')
                only_self = True

            if line.strip().startswith('self'):
                if 'self=None,' == line.strip():
                    line = line.replace('self=None', f'self: Optional[Union["{class_name}", Filter]] = None')
                line = line.replace(f'Union["{class_name}", Filter, None]', f'Optional[Union["{class_name}", Filter]]')
                line = line.replace('Filter', 'PFilter, Filter')

            if line.strip().startswith('filters') and line.endswith(',\n'):
                if 'filters=None,' == line.strip():
                    line = line.replace('filters=None', 'filters: Optional[Filter] = None')
                code_lines.append("\t\tclient_filters: Optional[Union[PFilter, Filter]] = None,\n")

            if 'pyrogram.Client.add_handler' in line:
                line = line.replace('pyrogram.Client.add_handler', 'pypoligram.ClientManager.add_handler')

            if (_line := line.strip()).startswith(':obj:`~pyrogram.handlers.') and _line.endswith('`.'):
                handler_name = _line.removeprefix(':obj:`~pyrogram.handlers.').removesuffix('`.')

            if line.strip().startswith('filters') and line.endswith(':\n'):
                code_lines.extend(CLIENT_FILTERS_DOCLINES)
            if '"""' == line.strip():
                try:
                    _index = code_lines.index('        Parameters:\n')
                    _index = code_lines.index('\t\tParameters:\n')
                except ValueError:
                    code_lines.extend(['\n', '\t\tParameters:\n'] + CLIENT_FILTERS_DOCLINES[:-1])

            if '~pyrogram.handlers' in line:
                delete_lines = 2

            if 'if isinstance(self, pyrogram.Client):' == line.strip():
                line = line.replace('pyrogram.Client', 'pypoligram.ClientManager')

            if line.strip().startswith('self.add_handler(pyrogram.handlers.'):
                if only_self:
                    line = f'\t\t\t\tself.add_handler(pyrogram.handlers.{handler_name}(func), client_filters or ALL)\n'
                else:
                    line = f'\t\t\t\tself.add_handler(pyrogram.handlers.{handler_name}(func, filters), client_filters or ALL, group)\n'

            if line.startswith('func.handlers.append') and line.endswith('))') and only_self:
                line = f'\t\t\t\tfunc.handlers.append((pyrogram.handlers.{handler_name}(func), client_filters or ALL, 0))\n'

            code_lines.append(line.replace('    ', '\t'))

            if 'from pyrogram.filters import Filter' == line.strip():
                code_lines.extend(IMPORT_LINES)

            if 'def decorator(func: Callable) -> Callable:' == line.strip():
                code_lines.append('\t\t\tnonlocal self, client_filters' + ('\n' if only_self else ', filters, group\n'))

            if 'func.handlers = []' == line.strip():
                code_lines.extend(SWAP_CODE_LINES[only_self])

            if class_name and f'pyrogram.handlers.{handler_name}(func, self),' == line.strip():
                line = f'\t\t\t\t\t\tpyrogram.handlers.{handler_name}(func, filters),\n'
                code_lines[-1] = line
                delete_lines = 1
                code_lines.extend(['\t\t\t\t\t\tclient_filters or ALL,\n', '\t\t\t\t\t\tgroup\n'])


    with poli_dec_path.open('w') as poli_dec_file:
        poli_dec_file.writelines(code_lines)

if pypoligram_dec.parent.name == 'pypoligram' and initpy_path.exists():
    pass
else:
    lines: dict[bool, list[str]] = {False: [], True: []}
    for module_name, ClassName in names:
        lines[False].append(INITPY_CONTENT[False].format(module_name, ClassName))
        lines[True].append(INITPY_CONTENT[True].format(ClassName))
    _ = initpy_path.write_text(
        INITPY_FILE.format(''.join(lines[False]), ''.join(lines[True]))
    )
