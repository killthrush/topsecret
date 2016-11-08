from flask_pymongo import PyMongo
from pymongo import MongoClient
from functools import wraps
import re

DEFAULT_PAGE_SIZE = 10


def requires_client(fn):
    """
    Ensures that a valid client connection is defined for a facade method
    :param fn: the function being wrapped
    :return: The wrapped method
    """
    def wrapper(self, *args, **kwargs):
        if not self._client:
            raise ValueError('No data source bound! Call bind_flask() or bind_client() first.')
        return fn(self, *args, **kwargs)
    return wraps(fn)(wrapper)


class DataFacade:
    """
    Facade to wrap select mongodb operations to keep the
    calling code nice, clean, and testable
    """
    def __init__(self, app=None, mongo_uri=None):
        """
        Initializer for the DataFacade class
        :param app: A flask app to provide context to the facade
        :return: None
        """
        self._client = None
        if app:
          self.bind_flask(app)

    def bind_flask(self, app, mongo_uri=None):
        """
        Creates a bound PyMongo client based on a flask context
        :param app: A flask app to provide context to the facade
        :param mongo_uri: A URI of a mongo instance to use with a connected client
        :return: None
        """
        if self.is_bound:
            raise TypeError("Client already bound.")
        self._client = PyMongo(app)

    def bind(self, mongo_uri):
        """
        Creates a bound PyMongo client based on a uri
        :param mongo_uri: A URI of a mongo instance to use with a connected client
        :return: None
        """
        if self.is_bound:
            raise TypeError("Client already bound.")
        self._client = MongoClient(mongo_uri)

    @property
    @requires_client
    def db(self):
        """
        Returns the native mongodb database reference
        for cases where the regular helpers are not needed.
        :return: The database reference
        """
        return self._client.db

    @property
    def is_bound(self):
        """
        Determines if a client is bound to the instance
        :return: True if the instance is bound, else False
        """
        return (self._client is not None)

    @requires_client
    def clear_collection(self, collection_name):
        """
        Deletes all documents in a collection.  Use with care!
        :param collection_name: The name of the collection to use
        :return: None
        """
        self._client.db[collection_name].delete_many({})

    @requires_client
    def load(self, collection_name, page=None, page_size=None, sort=None, **kwargs):
        """
        Loads documents from the given collection given a set of query arguments
        :param collection_name: The name of the collection to query
        :param kwargs: Query arguments
        :return: A list containing the matching documents (or an empty list)
        """
        if page is None:
            page = 1
        if page_size is None:
            page_size = DEFAULT_PAGE_SIZE
        if sort is None:
            sort = { "_id": 1 }

        projection = {
            "subject": "$subject",
            "body": "$body",
            "date": "$date",
            "sender": "$sender",
            "recipient": "$recipient",
            "attachments": "$attachments",
            "total_attachments": {
                "$size": "$attachments"
            }
        }

        pipe = [
            # {"$project": projection}
        ]

        if len(kwargs) > 0:
            pipe.append(self.build_match(kwargs))
        pipe.append({"$sort": sort})
        pipe.append({"$skip": (page - 1) * page_size})
        pipe.append({"$limit": page_size})

        collection = self._client.db[collection_name]
        result = list(collection.aggregate(pipeline=pipe, allowDiskUse=True))
        return result

    def build_match(self, parameters):
        match_dict = {}
        for parameter in parameters.items():
            value = re.compile(re.escape(parameter[1]))
            match_dict[parameter[0]] = {"$regex": value}
        return {
            "$match": match_dict
        }

    @requires_client
    def store(self, collection_name, document):
        """
        Store a document in the given collection.
        Create the collection if it does not exist.
        :param collection_name: The name of the collection to use
        :param document: The document to store
        :return: None
        """
        self._client.db[collection_name].insert_one(document)

