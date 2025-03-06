import os

STAGE = os.getenv("STAGE", "dev")
AWS_REGION = os.getenv("REGION")
AWS_BUCKET = os.getenv("BUCKET")

MONGO_HOSTNAME = os.getenv("MONGO_HOSTNAME")
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")

SERVICE_URL = os.getenv("SERVICE_URL")
IMAGE_URL = os.getenv("IMAGE_URL")
