#!/usr/bin/env python3
"""Generate pypoligram's ClientManager decorators from the installed kurigram.

The old ``build_decorators.py`` rewrites kurigram's source line by line. Whether a
patch lands depends on how black happened to wrap a line, which is why seven
decorators end up with 2-tuple registrations and all of them lose ``client_filters``.

This script reads kurigram with ``ast`` instead, keeps nothing from its source except
four facts (class, method, handler and docstring description) and renders three fixed
templates:

* ``update``  -- ``on_message`` and friends
* ``special`` -- ``on_start`` / ``on_stop`` / ``on_connect`` / ``on_disconnect``
* ``error``   -- ``on_error``

Every template shares the same registration tail, so the plugin/manager split exists
once here instead of 32 times in the output.

Usage::

    python devscripts/build_decorators2.py            # write downloads/decorators
    python devscripts/build_decorators2.py --release  # write pypoligram/decorators
    python devscripts/build_decorators2.py --check    # diff against pypoligram/decorators
"""

# Damn AI that wasn't bad. Anyway I tested it and it works as intended.
# Decorators still needs manual review but this script makes my job easier.
# Everything seemed normal I hope I am not wrong.

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Mapping

import pyrogram
import pyrogram.handlers

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = Path(pyrogram.__file__).parent / "methods" / "decorators"
DOWNLOAD_DIR = REPO_ROOT / "downloads" / "decorators"
RELEASE_DIR = REPO_ROOT / "pypoligram" / "decorators"
HELPER_SOURCE = RELEASE_DIR / "unbound_arguments.py"

Kind = Literal["update", "special", "error"]


@dataclass
class Spec:
    module: str
    class_name: str
    method: str
    handler: str
    kind: Kind
    summary: str
    parameters: Mapping[str, list[str]] = field(default_factory=dict)


# Reading kurigram


def _parse_parameters(docstring: str) -> dict[str, list[str]]:
    """Split the ``Parameters:`` section into ``{name: body lines}``."""
    parameters: dict[str, list[str]] = {}
    lines = docstring.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == "Parameters:")
    except StopIteration:
        return parameters

    name: str | None = None
    for line in lines[start + 1 :]:
        text = line.strip()
        if not text:
            continue
        if text.endswith("):"):
            name = text.split(" ", 1)[0]
            parameters[name] = []
        elif name is not None:
            parameters[name].append(text)
    return parameters


def read_spec(path: Path) -> Spec:
    tree = ast.parse(path.read_text(), filename=str(path))

    classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name.startswith("On")]
    if len(classes) != 1:
        raise SystemExit(f"{path.name}: expected one On* class, found {len(classes)}")
    cls = classes[0]

    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name.startswith("on_")]
    if len(methods) != 1:
        raise SystemExit(f"{path.name}: expected one on_* method, found {len(methods)}")
    fn = methods[0]

    args = {a.arg for a in (*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs)}

    handlers = {
        call.func.attr
        for call in ast.walk(fn)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr.endswith("Handler")
    }
    if len(handlers) != 1:
        raise SystemExit(f"{path.name}: expected one handler class, found {sorted(handlers)}")
    handler = handlers.pop()

    if not hasattr(pyrogram.handlers, handler):
        raise SystemExit(f"{path.name}: pyrogram.handlers has no {handler}")

    if "exceptions" in args:
        kind: Kind = "error"
    elif {"filters", "group"} <= args:
        kind = "update"
    elif args == {"self"}:
        kind = "special"
    else:
        raise SystemExit(f"{path.name}: unknown signature {sorted(args)}")

    docstring = ast.get_docstring(fn) or ""
    summary = docstring.splitlines()[0].strip() if docstring else f"Decorator for handling {path.stem[3:]}."

    return Spec(
        module=path.stem,
        class_name=cls.name,
        method=fn.name,
        handler=handler,
        kind=kind,
        summary=summary,
        parameters=_parse_parameters(docstring),
    )


def read_specs() -> list[Spec]:
    return [read_spec(path) for path in sorted(SOURCE_DIR.glob("on_*.py"))]


# Rendering


def _param(header: str, body: list[str]) -> list[str]:
    return [f"            {header}"] + [f"                {line}" for line in body]


def _call(prefix: str, args: str, indent: int = 12, width: int = 88) -> list[str]:
    pad = " " * indent
    one_line = f"{pad}{prefix}({args})"
    if len(one_line) <= width:
        return [one_line]
    return [f"{pad}{prefix}(", f"{pad}\t{args}", f"{pad})"]


def _filter_paragraph(spec: Spec) -> list[str]:
    return spec.parameters.get("filters") or [
        "Pass one or more filters to allow only a subset of updates to be passed",
        "in your function.",
    ]


def _exceptions_paragraph(spec: Spec) -> list[str]:
    return spec.parameters.get("exceptions") or [
        "An exception type or a sequence of exception types that this handler should handle.",
        "If None, the handler will catch any exception that is a subclass of ``Exception``.",
    ]


def render_signature(spec: Spec) -> list[str]:
    lines = ["    def %s(" % spec.method]
    if spec.kind == "special":
        lines += [
            f"        self: {spec.class_name} | PFilter | None = None,",
            "        client_filters: PFilter | None = None,",
        ]
    elif spec.kind == "update":
        lines += [
            f"        self: {spec.class_name} | PFilter | Filter | None = None,",
            "        client_filters: PFilter | Filter | None = None,",
            "        filters: Filter | None = None,",
            "        group: int = 0,",
        ]
    else:
        lines += [
            f"        self: {spec.class_name} | Exception | Sequence[Exception] | PFilter | Filter | None = None,",
            "        exceptions: Exception | Sequence[Exception] | None = None,",
            "        client_filters: PFilter | Filter | None = None,",
            "        filters: Filter | None = None,",
            "        group: int = 0,",
        ]
    lines.append("    ) -> Callable[[HandlerType], HandlerType]:")
    return lines


def render_docstring(spec: Spec) -> list[str]:
    lines = [
        f'        """{spec.summary}',
        "",
        "        This does the same thing as :meth:`~pypoligram.ClientManager.add_handler` using the",
        f"        :obj:`~pyrogram.handlers.{spec.handler}`.",
        "",
        "        Parameters:",
    ]

    if spec.kind == "error":
        lines += _param(
            "exceptions (``Exception`` | List of ``Exception``, *optional*):",
            _exceptions_paragraph(spec),
        )
        lines.append("")

    lines += _param(
        "client_filters (:obj:`~pypoligram.filters`, *optional*):",
        [
            "Pass one or more filters to allow only a subset of clients to be passed",
            "in your function.",
        ],
    )

    if spec.kind in ("update", "error"):
        lines.append("")
        lines += _param(
            "filters (:obj:`~pyrogram.filters`, *optional*):",
            _filter_paragraph(spec),
        )

    if spec.kind != "special":
        lines.append("")
        lines += _param("group (``int``, *optional*):", ["The group identifier, defaults to 0."])

    lines.append('        """')
    return lines


def render_body(spec: Spec) -> list[str]:
    handler = f"pyrogram.handlers.{spec.handler}"
    lines = ["", "        def decorator(func: HandlerType) -> HandlerType:"]

    if spec.kind == "update":
        lines += [
            "            arguments = unbound_arguments(",
            "                self,",
            "                client_filters=client_filters,",
            "                filters=filters,",
            "                group=group,",
            "            )",
        ]
        lines += _call(f"handler = {handler}", "func, arguments.filters")
    elif spec.kind == "special":
        lines += [
            "            arguments = unbound_arguments(",
            "                self,",
            "                client_filters=client_filters,",
            "                filters=None,",
            "                group=0,",
            "            )",
        ]
        lines += _call(f"handler = {handler}", "func")
    else:
        lines += [
            "            arguments = unbound_error_arguments(",
            "                self,",
            "                exceptions=exceptions,",
            "                client_filters=client_filters,",
            "                filters=filters,",
            "                group=group,",
            "            )",
        ]
        lines += _call(f"handler = {handler}", "func, arguments.exceptions, arguments.filters")

    lines += [
        "",
        "            if isinstance(self, pypoligram.ClientManager):",
        "                self.add_handler(",
        "                    handler, arguments.client_filters or ALL, arguments.group",
        "                )",
        "            else:",
        '                if not hasattr(func, "handlers"):',
        "                    func.handlers = []",
        "",
        "                func.handlers.append(",
        "                    (handler, arguments.client_filters or ALL, arguments.group)",
        "                )",
        "",
        "            return func",
        "",
        "        return decorator",
    ]
    return lines


def render_module(spec: Spec) -> str:
    helper = "unbound_error_arguments" if spec.kind == "error" else "unbound_arguments"

    imports = [
        "from __future__ import annotations",
        "",
        "from typing import TYPE_CHECKING",
        "",
        "import pyrogram",
        "",
        "import pypoligram",
        "from pypoligram.filters import ALL",
        "",
        f"from .unbound_arguments import {helper}",
        "",
        "if TYPE_CHECKING:",
    ]
    if spec.kind == "error":
        imports.append("    from collections.abc import Callable, Sequence")
    else:
        imports.append("    from collections.abc import Callable")

    imports.append("")
    if spec.kind in ("update", "error"):
        imports.append("    from pyrogram.filters import Filter")
    imports += [
        "    from pyrogram.methods.decorators.handler_type import HandlerType",
        "",
        "    from pypoligram.filters import Filter as PFilter",
        "",
        "",
        f"class {spec.class_name}:",
    ]

    lines = imports + render_signature(spec) + render_docstring(spec) + render_body(spec)
    return to_tabs("\n".join(lines) + "\n")


def render_init(specs: list[Spec]) -> str:
    modules = "".join(f"from .{spec.module} import {spec.class_name}\n" for spec in specs)
    bases = "".join(f"\t{spec.class_name},\n" for spec in specs)
    return f"{modules}\n\nclass Decorators(\n{bases}):\n\tpass\n"


def to_tabs(source: str) -> str:
    """Turn 4-space indentation into the tabs the rest of the repo uses."""
    lines = []
    for line in source.splitlines():
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        lines.append("\t" * (indent // 4) + " " * (indent % 4) + stripped)
    return "\n".join(lines) + "\n"


def render_all(specs: list[Spec]) -> dict[str, str]:
    rendered = {spec.module + ".py": render_module(spec) for spec in specs}
    rendered["__init__.py"] = render_init(specs)
    return rendered


# Validation


def validate(specs: list[Spec], rendered: dict[str, str]) -> None:
    upstream = {path.name for path in SOURCE_DIR.glob("on_*.py")}
    produced = {spec.module + ".py" for spec in specs}
    if upstream != produced:
        raise SystemExit(
            f"upstream/render mismatch: missing={sorted(upstream - produced)} "
            f"extra={sorted(produced - upstream)}"
        )

    for name, source in rendered.items():
        try:
            compile(source, name, "exec")
        except SyntaxError as error:
            raise SystemExit(f"{name}:{error.lineno}: {error.msg}") from None


def describe(specs: list[Spec]) -> str:
    counts = {kind: sum(spec.kind == kind for spec in specs) for kind in ("update", "special", "error")}
    return (
        f"kurigram {pyrogram.__version__}: {len(specs)} decorators "
        f"({counts['update']} update, {counts['special']} special, {counts['error']} error)"
    )


# Writing


def write(target: Path, rendered: dict[str, str], *, copy_helper: bool) -> None:
    target.mkdir(parents=True, exist_ok=True)

    for name, source in rendered.items():
        (target / name).write_text(source)

    expected = set(rendered) - {"__init__.py"}
    for stale in sorted(target.glob("on_*.py")):
        if stale.name not in expected:
            stale.unlink()
            print(f"removed {stale}")

    if copy_helper and HELPER_SOURCE.exists():
        (target / HELPER_SOURCE.name).write_text(HELPER_SOURCE.read_text())

    print(f"wrote {len(rendered) - 1} decorators + __init__.py to {target}")


def check(rendered: dict[str, str]) -> int:
    if not RELEASE_DIR.exists():
        print(f"{RELEASE_DIR} does not exist", file=sys.stderr)
        return 1

    drift = []
    for name, source in rendered.items():
        path = RELEASE_DIR / name
        if not path.exists():
            drift.append(f"missing  {name}")
        elif path.read_text() != source:
            drift.append(f"differs  {name}")

    expected = set(rendered)
    for path in sorted(RELEASE_DIR.glob("on_*.py")):
        if path.name not in expected:
            drift.append(f"unexpected {path.name}")

    if drift:
        print("\n".join(drift))
        print(f"\n{len(drift)} file(s) out of date; run with --release")
        return 1

    print(f"up to date: {len(rendered) - 1} decorators + __init__.py")
    return 0


# CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--release", action="store_true", help="write pypoligram/decorators")
    group.add_argument("--check", action="store_true", help="diff against pypoligram/decorators")
    args = parser.parse_args(argv)

    specs = read_specs()
    rendered = render_all(specs)
    validate(specs, rendered)
    print(describe(specs))

    if args.check:
        return check(rendered)

    target = RELEASE_DIR if args.release else DOWNLOAD_DIR
    write(target, rendered, copy_helper=not args.release)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
