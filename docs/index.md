Documentation for Orwynn Web Framework.

## Table Of Contents

1. [Tutorials](tutorials.md)
2. [How-To Guides](howto.md)
3. [Reference](reference.md)
4. [Explanation](explanation.md)

## Key Features

### Modular

Orwynn uses [modules][orwynn.base.module.module.Module] as the main building blocks.

Each module contains a set of [services][orwynn.base.service.service.Service], [configs][orwynn.base.config.config.Config], [controllers][orwynn.base.controller.controller.Controller] and other objects are injectable (see [Dependency Injection](di.md)) to each other only within the same module or via the [import system][import-system].

### Dependency Injection

Each [module][orwynn.base.module.module.Module] has a set of [Providers][orwynn.di.provider.Provider] and [Acceptors][orwynn.di.acceptor.Acceptor].

Providers can be requested by Acceptors or other Providers as dependencies in the requestor's `__init__` method:
```py
class MyProvider(Service):
    ...

class MyAcceptor(Controller):
    def __init__(
        self,
        myprovider: MyProvider
    ):
        ...
```

The name of the argument doesn't matter, the type does.

See more about [DI system](di.md).

### FastAPI as an underlying engine

Orwynn utilizes and supports many features available in [FastAPI](https://fastapi.tiangolo.com/), including OpenAPI auto-documentation, modern Python support, WebSockets out of the box, CORS and many more.
