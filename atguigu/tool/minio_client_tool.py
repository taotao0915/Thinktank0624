import json

from minio import Minio

from config.config import MinioConfig

minio_client = None

def get_minio_client():
    global minio_client
    if minio_client is None:
        minio_client = Minio(
            endpoint=MinioConfig.minio_endpoint,
            access_key=MinioConfig.minio_access_key,
            secret_key=MinioConfig.minio_secret_key,
            secure=False
        )

        bucket_name = MinioConfig.minio_bucket_name
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        # 权限（设置权限）
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                    "Resource": f"arn:aws:s3:::{bucket_name}",
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                },
            ],
        }
        minio_client.set_bucket_policy(bucket_name, json.dumps(policy))

    return minio_client


if __name__ == "__main__":
    minio_client = get_minio_client()
    print(minio_client)
