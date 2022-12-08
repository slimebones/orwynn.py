from __future__ import annotations
from abc import ABCMeta
from typing import TypeVar

from src.base.node.node import Node


SingletonInstance = TypeVar("SingletonInstance")


class SingletonMeta(type):
    """Singleton metaclass for implementing singleton patterns. 
    
    See:
        https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """
    instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.instances:
            cls.instances[cls] = super().__call__(*args, **kwargs)
        return cls.instances[cls]


class Singleton(Node, metaclass=SingletonMeta):
    """Singleton base class."""
    @classmethod
    def ie(cls: type[SingletonInstance]) -> SingletonInstance:
        """Gets the single instance of the Singleton.
        
        Returns:
            Instance the Singleton holds.
        """
        return cls()