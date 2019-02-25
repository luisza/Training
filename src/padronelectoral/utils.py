from pymongo import MongoClient
from crpadron import settings


class MongoClientUtil:
    """
    This util class is to create an instance of mongo client.
    """
    client = None

    @classmethod
    def getInstance(cls):
        if cls.client is None:
            cls.client = MongoClient(settings.MONGOSERVER,
                                     username=settings.MONGOUSERNAME,
                                     password=settings.MONGOPASSWORD)
        return cls.client
