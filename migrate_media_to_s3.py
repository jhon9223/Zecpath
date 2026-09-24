import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
MEDIA_ROOT = BASE_DIR / "media"

bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")
region_name = os.getenv("AWS_S3_REGION_NAME")

s3 = boto3.client(
    "s3",
    region_name=region_name,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

if not MEDIA_ROOT.exists():
    print("media/ folder does not exist.")
    raise SystemExit

files = [path for path in MEDIA_ROOT.rglob("*") if path.is_file()]

print(f"Found {len(files)} files.")

for file_path in files:
    relative_path = file_path.relative_to(MEDIA_ROOT).as_posix()

    print(f"Uploading: {relative_path}")

    s3.upload_file(
        str(file_path),
        bucket_name,
        relative_path,
    )

print("Migration completed successfully.")
