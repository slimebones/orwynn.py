from orwynn.base.service.framework_service import FrameworkService


class DatabaseService(FrameworkService):
    """Responsible of working with chosen database.

    This is an abstract class since SQL and NoSQL databases vary in set of
    functionality, but some things are in common, which are desribed here.
    """
    pass
