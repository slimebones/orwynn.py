
from orwynn.base.service.service import Service


class Database(Service):
    """Represents a connection to database as well as set of actions with this
    database.

    This is an abstract class and defines core methods which should present on
    both SQL and NoSQL databases. Arguments for these core methods in turn vary
    depending on chosen database kind. For example actions for MongoDB will
    require specifying a collection to work with.

    Anyway, these methods for every service subclassing this one, will be
    incapsulated by Mappings. So the end user will work only with these
    mappings only.
    """
