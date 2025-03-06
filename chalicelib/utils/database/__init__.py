from chalicelib.database._mongodb import MongoDB
from chalicelib.constant.service import COLLECTION, CATEGORY, WINE
from chalicelib.settings import MONGO_DATABASE, MONGO_HOSTNAME, MONGO_PASSWORD, MONGO_USERNAME, STAGE

MONGODB = MongoDB(MONGO_HOSTNAME, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DATABASE)
