# Pypoligram
Pypoligram is a Python package designed to manage multiple `pyrogram.Client` instances efficiently. It simplifies the process of handling multiple clients.

> [!WARNING]
> For now only officially supported pyrogram fork is [kurigram](https://github.com/kurigram-org/kurigram). Even though I plan to support all known forks I don't have time nor energy to do that. If it does not work you I am trully sorry.

## Features

- Efficiently manage multiple `pyrogram.Client` instances with ease.
- Add or remove clients dynamically during runtime.
- Simplify Telegram account session management and event handling.
- Provide a unified interface for managing multiple Telegram API interactions.
- Streamline the process of registering handlers across multiple clients.
- Facilitate concurrent execution of multiple client sessions.

## Installation

Install pypoligram using pip:

```bash
pip install pypoligram
```

## Usage

Here's a quick example to get started:

```python
from pyrogram import Client
from pypoligram import ClientManager


# Example usage
manager = ClientManager([
    Client("session1"),
    Client("session2"),
    Client("session3")
])
manager.add_client(Client("other_session"))
... # register handlers
manager.run()
```

## Documentation

I don't know how to set a documentation page but I will write a [DOCUMENTATION.md](DOCUMENTATION.md).

## Contributions

Contributions are welcome! I don't have much information about developing a project, and I need help improving the documentation page. If you have any ideas or encounter any issues, please share them on the Issues and Pull Requests page. You can also star this project to motivate me and help me focus on it more.

## License

This project is licensed under the [GNU Lesser General Public License v3 or later (LGPLv3+)](COPYING.lesser).
