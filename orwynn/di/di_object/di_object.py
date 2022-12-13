from orwynn.di.di_object.acceptor import Acceptor
from orwynn.di.di_object.provider import Provider


# Any object which can be stored in DI container and should be presented in
# single instance there.
DIObject = Provider | Acceptor
