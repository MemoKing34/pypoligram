# PyPoligram Documentation

PyPoligram is a Python package designed to manage multiple `pyrogram.Client` instances efficiently. It simplifies the process of handling multiple clients and provides a unified interface for managing pyrogram interactions.

I tried to make it similar to Pyrogram. These methods have nearly the same usage as Pyrogram. Here, I will explain the differences.

---

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Core Classes](#core-classes)
   - [ClientManager](#clientmanager)
4. [Filters](#filters)
5. [Decorators](#decorators)
6. [Smart Plugins](#smart-plugins)
7. [Examples](#examples)

---

## Installation

Install PyPoligram using pip:

```bash
pip install pypoligram
```

---

## Getting Started

Here's a quick example to get started:

```python
from pyrogram import Client
from pypoligram import ClientManager

# Initialize the ClientManager with multiple clients
manager = ClientManager([
    Client("session1"),
    Client("session2"),
    Client("session3")
])

# Add another client dynamically
manager.add_client(Client("other_session"))

# Run the manager
manager.run()
```

---

## Core Classes

### ClientManager

The `ClientManager` class is the central component of PyPoligram. It allows you to manage and run multiple `pyrogram.Client` instances with a unified interface.

#### Parameters

* **`clients`** (`iterable`, *optional*):
  An iterable of `pyrogram.Client` instances to be managed. You can pass a `list`, `tuple`, `set`, or any other iterable.
  If not provided, the manager will start empty, and you can add clients later using `add_client`.

* **`name`** (`str`, *optional*):
  The name of the manager. Useful for identification or debugging purposes.
  Defaults to `"Clients"`.

* **`plugins`** (`dict`, *optional*):
  Smart Plugin settings to be applied to all clients.
  For example: `{"root": "plugins"}` will apply plugins from the specified path across all clients.
  This system extends Pyrogram's plugin support to work uniformly across multiple clients.
  *Defaults to `None`.*

* **`dont_modify`** (`bool`, *optional*):
  If `True`, the manager will **not** inject its custom behavior into clients.
  This means:

  * Handler functions won’t receive the `manager` argument.
  * The internal dispatcher won’t be replaced.
    Use this if you want to manage clients without altering their behavior.
    *Defaults to `False`.*

* **`kwargs`** (`dict`, *optional*):
  Keyword arguments that will be passed to all clients (unless a client already defines its own value for a specific key).
  Useful for setting shared options like `api_id`, `api_hash`, or `workdir`.
  *Defaults to `None`.*

#### Methods

* `add_client`: Adds a client to the manager. 
    Params:
    * `client: Client`: The client that will be added to the manager.
    * `dont_add_kwargs: bool`: If it sets to True `ClientManager.kwargs` values wont pass the client. _Optional, default: False_. 

* `discard_client`: Removes a client from the manager.
    Params:
    * `client: Client`: The client that will be removed from the manager.
        Note: You have to give **the exact client object**. If you give a different client with the same name as the client that will be removed **it WON'T work**, it will be ignored.

* `add_handler(filters, handler, group=0)`: Registers an update handler to multiple clients.
    Params:
    * `handler: pyrogram.handlers.Handler`: The handler that will be registired.
    * `filters: pypoligram.Filter`: The filter to filter the clients that will receive the handler. _Optional, default: `pypoligram.filters.ALL`_
    * `group: int`: The group identifier. _Optional, default: 0_.

* `remove_handler`: Removes a previously registered update handler. Just like with pyrogram's client object, you have to give the exact handler object.
    Params:
    * `handler: pyrogram.handlers.Handler`: The handler that will be removed.
    * `group: int`: This is the group identifier that the handler was registered with. _Optional, default: 0_.

* `start`: Starts all clients in the manager.
    Params:
    * `sequential: bool`: If it is set to True, clients will be started sequentially instead of concurrently. _Optional, default: False_

* `stop`: Stops all clients in the manager.
    Params:
    * `sequential: bool`: If it is set to True, clients will be stopped sequentially instead of concurrently. _Optional, default: False_
    * `block: bool`: Blocks the code execution until all the clients has been stopped. It is useful with ``block=False`` in case you want to stop the own client **within** a handler in order not to cause a deadlock. _Optional, default: True_

* `restart`: Restarts all clients in the manager. To do this, it will call the `Client.restart` method for each client.
    Params:
    * `sequential: bool`: If it is set to True, clients will be restarted sequentially instead of concurrently. _Optional, default: False_
    * `block: bool`: Blocks the code execution until all the clients has been restarted. It is useful with ``block=False`` in case you want to restart the own client **within** a handler in order not to cause a deadlock. _Optional, default: True_

* `restart2`: This is also restarts all the clients in the manager. But this fuction calls its own stop and start method instead of using `Client.restart` method. Params are same as `restart`

* `run`: Starts the manager, idles the main script, and stops the manager.
    Params:
    * `coroutine`: Coroutine object that will be runned instead of the manager. You can use it like `asyncio.run`. If nothing is given it will start the manager, idle the main script, and stop the manager, as mentioned previously.
    * `sequential: bool`: If it is set to True, clients will be started and stopped sequentially instead of concurrently. _Optional, default: False_
---


## Filters

Filters in PyPoligram allow you to filter clients based on custom logic. It works similarly to Pyrogram's filter system. However, there are two differences. First, you have to use synchronous functions. Second, these filters run only once when the `ClientManager.add_handler` function runs. If you need to filter dynamically, you can access the manager from its clients via the `_clients` parameter.

### Built-in Filters

* `ALL`: Matches all clients.
* `USER`: Matches user clients (non-bot clients).
* `BOT`: Matches bot clients.
* `client(names)`: Matches clients by their `name` attribute.

### Usage of the filters

```python
from pyrogram import Client
from pyrogram.handlers import MessageHandler
from pypoligram import ClientManager, filters as pfilters # To avoid confusion, we recommend using PyPoligram's filters as pfilters, even if you are not using Pyrogram's filters.

manager = ClientManager([
    Client("user"),
    Client("groot"),
    Client("bot")
])

def echo(manager, client, message):
    message.reply(message.text)

def iamgroot(manager, client, message):
    message.reply("I AM GROOT!")

manager.add_handler(pfilters.BOT, MessageHandler(echo))
manager.add_handler(pfilters.client("groot"), MessageHandler(iamgroot))

manager.run()
```

### Creating Custom Filters

Just like Pyrogram's, you can create custom filters using the `create` function:

```python
from pypoligram.filters import create

def my_filter(_, __, client):
    return client.name == "specific_client"

MY_FILTER = create(my_filter, "MY_FILTER")
```

---

## Decorators

Similar to pyrogram's, PyPoligram provides decorators that simplify the process of registering handlers for multiple clients.

### Available Decorators

* `on_message`: Handles incoming messages.
* `on_edited_message`: Handles edited messages.
* `on_deleted_messages`: Handles deleted messages.
* `on_callback_query`: Handles callback queries.
* `on_chosen_inline_result`: Handles chosen inline results.
* `on_inline_query`: Handles inline queries.
* `on_poll`: Handles polls.
* `on_user_status`: Handles user status changes.
* `on_chat_member_updated`: Handles chat member updates.
* `on_chat_join_request`: Handles chat join requests.
* `on_disconnect`: Handles client disconnections.
* `on_chat_boost`: Handles chat boost events.
* `on_message_reaction`: Handles reactions to messages.
* `on_message_reaction_count`: Handles changes in message reaction counts.
* `on_purchased_paid_media`: Handles events related to purchased paid media.
* `on_pre_checkout_query`: Handles pre-checkout queries in payments.
* `on_shipping_query`: Handles shipping queries in payments.
* `on_story`: Handles stories.
* `on_raw_update`: Handles raw updates directly from Telegram.

---

### Example Usage

```python
from pyrogram import Client
from pypoligram import ClientManager

manager = ClientManager()
manager.add_client(Client("my_account"))

@ClientManager.on_message()
async def handle_message(manager, client, message):
    print(f"Received message: {message.text}")

manager.run()
```

---

## Smart Plugins

PyPoligram supports **Smart Plugins**, a powerful plugin system that allows you to modularize handler logic across multiple files and folders. It helps you keep your codebase clean and organized, especially when working with many clients and handlers.

> 💡 **Tip:** Smart Plugins are **optional** and disabled by default. You must explicitly enable them by passing the `plugins` parameter to `ClientManager`.


### Why Use Smart Plugins?

With Smart Plugins:

* You don't need to manually `add_handler()` functions.
* You can organize your handlers in plugin folders using decorators.
* Handlers are automatically registered across **all clients**.


### Folder Structure Example

```
myproject/
├── plugins/
│   └── handlers.py
└── main.py
```

**plugins/handlers.py**

```python
from pypoligram import ClientManager
from pyrogram import filters

@ClientManager.on_message(filters.private)
async def echo(manager, client, message):
    await message.reply(message.text)

@ClientManager.on_message(filters.private, group=1)
async def reverse(manager, client, message):
    await message.reply(message.text[::-1])
```

**main.py**

```python
from pyrogram import Client
from pypoligram import ClientManager

# Enable Smart Plugins
plugins = dict(root="plugins")

manager = ClientManager(
    [Client("session1"), Client("session2")],
    plugins=plugins
)

manager.run()
```


### Controlling What Plugins Load

You can fine-tune which plugins load using `include` and `exclude`:

```python
plugins = dict(
    root="plugins",
    include=[
        "handlers.echo",
        "subfolder.module fn2 fn1"  # Load only fn2 and fn1 in that order
    ],
    exclude=[
        "debug.crashy_handler"
    ]
)
```

* `include`: Only these plugins and functions will be loaded.
* `exclude`: These will be skipped.
* You can define the **function load order** within a module (`fn2 fn1`).


### Using Smart Plugins with ClientManager

Smart Plugins are passed through the `plugins` parameter of each `Client` you add to `ClientManager`. Once configured, the manager handles plugin loading across all clients.

```python
from pyrogram import Client
from pypoligram import ClientManager

plugins = dict(root="plugins")

manager = ClientManager([
    Client("acc1"),
    Client("acc2")
], plugins=plugins)

manager.run()
```

---

## Compatibility with Other Modules/Plugins/Forks

### Pyrogram Forks

Pypoligram should be fine with other pyrogram forks unless they have a different name. If your fork has a different name like [hydrogram](https://github.com/hydrogram/hydrogram) or [pyrofork](https://github.com/Mayuri-Chan/pyrofork), if you install pyrogram, everything (I didn't test it but) should work without any problems. I will add support for these forks later, but for now, I guess you should be fine with just by installing pyrogram.

### Pyromod

Pypoligram does not work with Pyromod unless you set the `dont_modify` parameter to `True` in `ClientManager`. This is because Pypoligram, by default, replaces `pyrogram.Client`'s dispatcher class with its own in order to pass the `ClientManager` client as a parameter to handler functions. 

On the other hand, Pyromod modifies the handlers to catch messages, and assumes (understandably) that handlers receive two parameters. However, when you change the dispatcher, handlers receive three parameters, which causes a conflict.

Currently, I am working on a [fork of Pyromod](https://github.com/MemoKing34/pyromod) that avoids modifying the handlers. Instead, it modifies the dispatcher. I believe this approach will be faster and more compatible with Pyrogram.

In addition to that, I plan to add support for [my own fork](https://github.com/MemoKing34/pyromod), since my implementation also modifies the dispatcher class.

For now, If you want to use pyromod, create you manager like this:
```python
manager = ClientManager(..., dont_modify=True)
```

### Others

At the moment, I am not aware of any other fork, module, or plugin for **Pyrogram** that has been tested with **Pypoligram**. I cannot guarantee compatibility with any of them.

If you know of a fork, module, or plugin that works with Pypoligram — or if you maintain one — feel free to let me know. I’ll be happy to test it, and if it doesn’t work, I’ll try to add support for it or include it in a compatibility list.

---

## Examples

### Registering Handlers

```python
from pyrogram import Client
from pyrogram.handlers import MessageHandler
from pypoligram import ClientManager, filters as pfilters

async def hello(client, message):
    print(message)

manager = ClientManager([
    Client("my_account1"),
    Client("my_account2"),
])

manager.add_handler(pfilters.client("my_account1"), MessageHandler(hello))
manager.run()
```
