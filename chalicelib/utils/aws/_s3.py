import gzip
import boto3


class S3:
    def __init__(self, stage: str, region: str, bucket: str):
        self.stage = stage
        self.region = region
        self.bucket = bucket
        self.client = boto3.client(region_name=self.region, service_name="s3")
        
    def head_object(self, key):
        response = self.client.head_object(Bucket=self.bucket, Key=key)
        return response["DeleteMarker"]

    def put_bucket_with_gzip(self, key, data, **kwargs):
        extra_args = kwargs.get("extra_args", {})
        extra_args["ContentEncoding"] = "gzip"
        extra_args["ServerSideEncryption"] = "AES256"

        return self.client.put_object(Bucket=self.bucket, Key=f"{self.stage}/{key}", Body=gzip.compress(data), **extra_args)

    def put_object(self, key, data, **kwargs):
        extra_args = kwargs.get("extra_args", {})
        extra_args["ServerSideEncryption"] = "AES256"

        print(f"{self.stage}/{key}")
        return self.client.put_object(
            Bucket=self.bucket,
            Key=f"{self.stage}/{key}",
            Body=data,
            **extra_args)

    def upload_file(self, byte_data, key, **kwargs):
        extra_args = kwargs.get("extra_args", {})
        extra_args["ServerSideEncryption"] = "AES256"

        return self.client.upload_fileobj(byte_data, self.bucket, f"{self.stage}/{key}", ExtraArgs=extra_args)

    def get_object(self, key, decompress=False):
        full_key = f"{self.stage}/{key}"
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=full_key)
            data = response['Body'].read()

            # ContentEncoding 헤더 확인
            content_encoding = response.get('ContentEncoding', '')

            if decompress or content_encoding == 'gzip':
                try:
                    data = gzip.decompress(data)
                    print(f"Successfully decompressed data from {full_key}.")
                except gzip.BadGzipFile:
                    print(f"Data from {full_key} is not valid gzip format.")
            else:
                print(f"Successfully fetched data from {full_key} without decompression.")
            return data
        except Exception as e:
            print(f"Failed to fetch {full_key} from S3: {e}")
            return None