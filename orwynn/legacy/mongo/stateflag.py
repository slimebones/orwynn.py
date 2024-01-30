from orwynn.mongo.document import Document


class MongoStateFlag(Document):
    key: str
    value: bool
