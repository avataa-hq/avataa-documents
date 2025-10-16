import pymongo.mongo_client

import settings


class Database:
    def __init__(self, host, port, username: str, password: str, database: str):
        self.__username = username
        self.__password = password
        self.__database = database
        self._host = host
        self._port = port
        self._client = None
        self._db = None
        self._document = None
        self._document_specification = None
        self._permissions = None

    def __init_db(self):
        self._client = pymongo.mongo_client.MongoClient(
            host=self._host,
            port=int(self._port),
            username=self.__username,
            password=self.__password,
            authSource=self.__database,
        )
        self._db = pymongo.mongo_client.database.Database = self._client[
            self.__database
        ]
        self._document: pymongo.mongo_client.database.Collection = self._db[
            "document"
        ]
        self._document_specification: pymongo.mongo_client.database.Collection = self._db[
            "document_specification"
        ]
        self._permissions: pymongo.mongo_client.database.Collection = self._db[
            "permissions"
        ]
        del self.__username
        del self.__password
        del self.__database

    @property
    def client(self):
        if self._client is None:
            self.__init_db()
        return self._client

    @property
    def db(self):
        if self._db is None:
            self.__init_db()
        return self._client

    @property
    def document(self) -> pymongo.mongo_client.database.Collection:
        if self._document is None:
            self.__init_db()
        return self._document

    @property
    def document_specification(self):
        if self._document_specification is None:
            self.__init_db()
        return self._document_specification

    @property
    def permissions(self):
        if self._permissions is None:
            self.__init_db()
        return self._permissions


db = Database(
    settings.MONGO_URL,
    settings.MONGO_PORT,
    settings.MONGO_USER,
    settings.MONGO_PASSWORD,
    settings.MONGO_DATABASE,
)
