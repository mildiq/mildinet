from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from application.common.media import MediaType
from application.dto.media import Media
from application.interfaces.dm.media import IMediaDm
from infra.common.transaction import TransactionManager
from infra.dm.mappers.media import map_media
from infra.orm.media import MediaOrm


@dataclass(kw_only=True, slots=True)
class MediaDm(IMediaDm):
    _tm: TransactionManager

    async def create(
            self,
            *,
            owner_id: int,
            stored_object_id: int,
            original_filename: str,
            media_type: MediaType,
    ) -> Media:
        orm = MediaOrm(
            owner_id=owner_id,
            stored_object_id=stored_object_id,
            original_filename=original_filename,
            media_type=media_type,
        )

        self._tm.add(instance=orm)
        await self._tm.flush(instances=[orm])

        query = (
            select(MediaOrm)
            .options(selectinload(MediaOrm.stored_object))
            .where(MediaOrm.id == orm.id)
        )

        result = await self._tm.execute(statement=query)
        orm = result.scalar_one()

        return map_media(orm=orm)

    async def get_by_id(
            self,
            *,
            media_id: int,
            for_update: bool = False,
    ) -> Media | None:
        query = (
            select(MediaOrm)
            .options(selectinload(MediaOrm.stored_object))
            .where(MediaOrm.id == media_id)
        )

        result = await self._tm.execute(statement=query)
        orm = result.scalar_one()

        if orm is None:
            return None

        return map_media(orm=orm)

    async def list(
        self,
        *,
        owner_id: int | None = None,
        media_ids: Sequence[int] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Media, ...]:
        query = (
            select(MediaOrm)
            .options(selectinload(MediaOrm.stored_object))
        )

        if owner_id is not None:
            query = query.where(MediaOrm.owner_id == owner_id)

        if media_ids is not None:
            query = query.where(MediaOrm.id.in_(media_ids))

        query = query.limit(limit).offset(offset)

        rows = (
            await self._tm.execute(statement=query)
        ).scalars().all()

        return tuple(map_media(orm=row) for row in rows)

    async def list_by_owner(
        self,
        *,
        owner_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Media, ...]:
        rows = (
            await self._tm.execute(
                statement=(
                    select(MediaOrm)
                    .options(selectinload(MediaOrm.stored_object))
                    .where(MediaOrm.owner_id == owner_id)
                    .order_by(MediaOrm.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                )
            )
        ).scalars().all()

        return tuple(map_media(orm=row) for row in rows)

    async def count_by_stored_object(
        self,
        *,
        stored_object_id: int,
    ) -> int:
        query = select(func.count(MediaOrm.id)).where(
            MediaOrm.stored_object_id == stored_object_id,
        )

        result = await self._tm.execute(statement=query)

        return result.scalar_one()

    async def delete(self, *, media_id: int) -> None:
        orm = await self._tm.get(entity=MediaOrm, identifier=media_id)
        if orm is None:
            return

        await self._tm.delete(instance=orm)
        await self._tm.flush()