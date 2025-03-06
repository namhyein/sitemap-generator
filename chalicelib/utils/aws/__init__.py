from chalicelib.utils.aws._s3 import S3
from chalicelib.settings import AWS_BUCKET, AWS_REGION, STAGE


BUCKET = S3(STAGE, AWS_REGION, AWS_BUCKET)
