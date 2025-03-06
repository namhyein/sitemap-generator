from typing import Any, Dict, List, Optional, Tuple, Union

import certifi
from pymongo import MongoClient, ReadPreference
from pymongo.database import Database
from pymongo.errors import PyMongoError
from pymongo.results import UpdateResult, BulkWriteResult

_MongoDBDocs = Dict[str, Union[str, int, Any]]


class MongoDB:
    def __init__(self, host: str, username: str, password: str, database: str):
        self._client = self._open_client(host, username, password)
        self._read_db = self._get_secondary_database(database)
        self._write_db = self._get_primary_database(database)

    def _open_client(self, host: str, username: str, password: str) -> MongoClient:
        return MongoClient(
            f"mongodb+srv://{username}:{password}@{host}",
            compressors="zstd",
            maxPoolSize=100,
            tlsCAFile=certifi.where()
        )

    def _get_primary_database(self, database: str) -> Database:
        return self._client[database]

    def _get_secondary_database(self, database: str) -> Database:
        return self._client.get_database(
            name=database, read_preference=ReadPreference.SECONDARY_PREFERRED
        )

    def _close_client(self):
        self._client.close()

    def get_document(self, collection: str, query: _MongoDBDocs, projection: _MongoDBDocs) -> _MongoDBDocs:
        doc = self._read_db.get_collection(collection).find_one(
            query, projection
        )
        return dict(doc) if (doc is not None) else dict()

    def aggregate_documents(self, collection: str, pipelines: List[_MongoDBDocs]) -> List[_MongoDBDocs]:
        docs = self._read_db.get_collection(collection).aggregate(pipelines)
        return list(docs) if (docs is not None) else []

    def get_documents(self, collection: str, query: _MongoDBDocs, projection: _MongoDBDocs, sort: Optional[List[Tuple[str, int]]] = None, limit: Optional[int] = None, skip: int = 0) -> List[Dict[str, Any]]:
        if sort and limit:
            docs = (
                self._read_db.get_collection(collection)
                .find(query, projection)
                .sort(sort)
                .skip(skip)
                .limit(limit)
            )
        elif sort:
            docs = (
                self._read_db.get_collection(collection)
                .find(query, projection)
                .skip(skip)
                .sort(sort)
            )
        elif limit:
            docs = (
                self._read_db.get_collection(collection)
                .find(query, projection)
                .skip(skip)
                .limit(limit)
            )
        else:
            docs = self._read_db.get_collection(collection).find(
                query, projection
            ).skip(skip)

        return list(docs) if (docs is not None) else []

    def upsert_document(
        self,
        collection: str,
        query: _MongoDBDocs,
        update_query: _MongoDBDocs
    ) -> Any:
        doc = self._write_db[collection].update_one(query, update_query, upsert=True)
        if not doc.acknowledged:
            raise PyMongoError("DB Upsert Error")
        return doc.upserted_id

    def update_document(
        self,
        collection: str,
        query: _MongoDBDocs,
        update_query: _MongoDBDocs
    ) -> UpdateResult:
        doc = self._write_db[collection].update_one(query, update_query, upsert=False)
        if not doc.acknowledged:
            raise PyMongoError("DB Update Error")
        return doc

    def update_documents(
        self,
        collection: str,
        query: _MongoDBDocs,
        update_query: _MongoDBDocs
    ) -> UpdateResult:
        doc = self._write_db[collection].update_many(query, update_query, upsert=False)
        if not doc.acknowledged:
            raise PyMongoError("DB Update Error")
        return doc

    def create_document(
        self,
        collection: str,
        document: _MongoDBDocs
    ) -> Any:
        doc = self._write_db[collection].insert_one(document=document)
        if not doc.acknowledged:
            raise PyMongoError("DB Insert Error")
        return doc.inserted_id

    def bulk_update_documents(
        self,
        collection: str,
        bulk_operations: list
    ) -> BulkWriteResult:
        doc = self._write_db[collection].bulk_write(bulk_operations)
        if not doc.acknowledged:
            raise PyMongoError("DB Update Error")
        return doc
