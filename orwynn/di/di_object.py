from orwynn.di.acceptor import Acceptor
from orwynn.di.provider import Provider


# Any object which can be stored in DI container and should be presented in
# single instance there.
DIObject = Provider | Acceptor
