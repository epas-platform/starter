"""BlobStore abstraction for object storage.

Provides a unified interface for blob/object storage regardless of
the underlying provider (S3, Azure Blob, MinIO, local filesystem).
"""

import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel

from app.config import get_settings


class BlobMetadata(BaseModel):
    """Metadata for a stored blob."""

    key: str
    size: int
    content_type: str
    checksum_sha256: Optional[str] = None
    created_at: Optional[datetime] = None
    etag: Optional[str] = None


class BlobStore(ABC):
    """Abstract base class for blob/object storage.

    All keys should be namespaced appropriately (e.g., by tenant_id)
    before being passed to these methods.
    """

    @abstractmethod
    async def put(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict[str, str]] = None,
    ) -> BlobMetadata:
        """Store a blob.

        Args:
            key: Object key/path
            data: Binary data to store
            content_type: MIME type
            metadata: Optional custom metadata

        Returns:
            Metadata about the stored object
        """
        pass

    @abstractmethod
    async def get(self, key: str) -> tuple[bytes, BlobMetadata]:
        """Retrieve a blob.

        Args:
            key: Object key/path

        Returns:
            Tuple of (data, metadata)

        Raises:
            KeyError: If object not found
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a blob.

        Args:
            key: Object key/path
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a blob exists.

        Args:
            key: Object key/path

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate a presigned URL for direct access.

        Args:
            key: Object key/path
            expiration: URL expiration in seconds
            method: HTTP method (GET or PUT)

        Returns:
            Presigned URL string
        """
        pass

    @abstractmethod
    async def list_objects(
        self,
        prefix: str = "",
        max_keys: int = 1000,
    ) -> list[BlobMetadata]:
        """List objects with optional prefix filter.

        Args:
            prefix: Key prefix to filter by
            max_keys: Maximum number of keys to return

        Returns:
            List of object metadata
        """
        pass


class S3BlobStore(BlobStore):
    """BlobStore implementation using S3 (or LocalStack S3)."""

    def __init__(
        self,
        bucket: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        region: Optional[str] = None,
    ):
        """Initialize the blob store.

        Args:
            bucket: S3 bucket name
            endpoint_url: Override endpoint (for LocalStack)
            region: AWS region
        """
        settings = get_settings()

        self._bucket = bucket or settings.s3_uploads_bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url or settings.aws_endpoint_url,
            region_name=region or settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    async def put(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict[str, str]] = None,
    ) -> BlobMetadata:
        """Store a blob in S3."""
        # Calculate checksum
        checksum = hashlib.sha256(data).hexdigest()

        put_args = {
            "Bucket": self._bucket,
            "Key": key,
            "Body": data,
            "ContentType": content_type,
        }

        if metadata:
            put_args["Metadata"] = metadata

        response = self._client.put_object(**put_args)

        return BlobMetadata(
            key=key,
            size=len(data),
            content_type=content_type,
            checksum_sha256=checksum,
            etag=response.get("ETag", "").strip('"'),
        )

    async def get(self, key: str) -> tuple[bytes, BlobMetadata]:
        """Retrieve a blob from S3."""
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            data = response["Body"].read()

            return data, BlobMetadata(
                key=key,
                size=response["ContentLength"],
                content_type=response.get("ContentType", "application/octet-stream"),
                etag=response.get("ETag", "").strip('"'),
                created_at=response.get("LastModified"),
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise KeyError(f"Object not found: {key}")
            raise

    async def delete(self, key: str) -> None:
        """Delete a blob from S3."""
        self._client.delete_object(Bucket=self._bucket, Key=key)

    async def exists(self, key: str) -> bool:
        """Check if a blob exists in S3."""
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError:
            return False

    async def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate a presigned URL for S3 object."""
        client_method = "get_object" if method == "GET" else "put_object"

        return self._client.generate_presigned_url(
            client_method,
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expiration,
        )

    async def list_objects(
        self,
        prefix: str = "",
        max_keys: int = 1000,
    ) -> list[BlobMetadata]:
        """List objects in S3 bucket."""
        response = self._client.list_objects_v2(
            Bucket=self._bucket,
            Prefix=prefix,
            MaxKeys=max_keys,
        )

        objects = []
        for obj in response.get("Contents", []):
            objects.append(
                BlobMetadata(
                    key=obj["Key"],
                    size=obj["Size"],
                    content_type="application/octet-stream",  # Not available in list
                    etag=obj.get("ETag", "").strip('"'),
                    created_at=obj.get("LastModified"),
                )
            )

        return objects


def get_blob_store(bucket: Optional[str] = None) -> BlobStore:
    """Factory function to get appropriate BlobStore implementation."""
    return S3BlobStore(bucket=bucket)
