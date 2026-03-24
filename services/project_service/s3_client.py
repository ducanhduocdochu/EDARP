import os
import uuid

import boto3
from botocore.exceptions import ClientError
from flask import current_app


def _get_client():
    return boto3.client(
        "s3",
        endpoint_url=current_app.config["S3_ENDPOINT_URL"],
        aws_access_key_id=current_app.config["S3_ACCESS_KEY"],
        aws_secret_access_key=current_app.config["S3_SECRET_KEY"],
        region_name=current_app.config.get("S3_REGION", "us-east-1"),
    )


def _bucket():
    return current_app.config["S3_BUCKET"]


def _ensure_bucket():
    client = _get_client()
    try:
        client.head_bucket(Bucket=_bucket())
    except ClientError:
        client.create_bucket(Bucket=_bucket())


def build_s3_key(tenant_id: str, project_id: str, file_name: str) -> str:
    """Build path: {tenant_id}/{project_id}/{uuid}_{file_name}"""
    unique = uuid.uuid4().hex[:8]
    safe_name = file_name.replace(" ", "_")
    return f"{tenant_id}/{project_id}/{unique}_{safe_name}"


def upload_file(file_obj, tenant_id: str, project_id: str, file_name: str) -> str:
    """Upload file to S3 and return the full s3 path."""
    _ensure_bucket()
    client = _get_client()
    key = build_s3_key(tenant_id, project_id, file_name)
    client.upload_fileobj(file_obj, _bucket(), key)
    return f"s3://{_bucket()}/{key}"


def delete_file(s3_path: str):
    """Delete a file from S3 by its full s3:// path."""
    if not s3_path or not s3_path.startswith("s3://"):
        return
    client = _get_client()
    path = s3_path.replace(f"s3://{_bucket()}/", "")
    client.delete_object(Bucket=_bucket(), Key=path)


def generate_presigned_url(s3_path: str, expires_in: int = 3600) -> str | None:
    """Generate a presigned download URL."""
    if not s3_path or not s3_path.startswith("s3://"):
        return None
    client = _get_client()
    key = s3_path.replace(f"s3://{_bucket()}/", "")
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": _bucket(), "Key": key},
        ExpiresIn=expires_in,
    )
