from orwynn.src.base.service.root_service import RootService


class DatabaseService(RootService):
    """Responsible of working with chosen database.
    
    This is an abstract class since SQL and NoSQL databases vary in set of
    functionality, but some things are in common, which are desribed here.
    """
    pass