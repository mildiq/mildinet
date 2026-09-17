from collections.abc import AsyncIterator
from uuid import uuid4

from miniopy_async import Minio
from miniopy_async.error import S3Error

from io import BytesIO

from application.interfaces.storage import IFileStorage, StoredFile


class S3FileStorage(IFileStorage):
    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool = False
    ) -> None:
        endpoint = (
            endpoint.removeprefix("http://")
                    .removeprefix("https://")
                    .rstrip("/")
        )

        self._bucket = bucket

        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    async def ensure_bucket(self) -> None:
        exists = await self._client.bucket_exists(self._bucket)
        if not exists:
            await self._client.make_bucket(self._bucket)

    async def upload(
        self,
        *,
        data: bytes,
        content_type: str,
        extension: str,
    ) -> StoredFile:
        key = f"posts/{uuid4().hex}.{extension}"

        stream = BytesIO(data)

        await self._client.put_object(
            bucket_name=self._bucket,
            object_name=key,
            data=stream,
            length=len(data),
            content_type=content_type,
        )

        return StoredFile(
            storage_key=key,
            content_type=content_type,
            size=len(data),
        )

    async def download(
        self,
        *,
        storage_key: str,
    ) -> AsyncIterator[bytes]:
        response = await self._client.get_object(
            self._bucket,
            storage_key,
        )

        try:
            async for chunk in response.content.iter_chunked(1024 * 1024):
                yield chunk

        finally:
            response.close()
            await response.release()

    async def delete(self, *, storage_key: str) -> None:
        try:
            await self._client.remove_object(self._bucket, storage_key)
        except S3Error:
            pass
