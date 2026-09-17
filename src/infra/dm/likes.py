from dataclasses import dataclass

from sqlalchemy import select

from application.interfaces.dm.likes import IPostLikeDm, ICommentLikeDm
from infra.common.transaction import TransactionManager
from infra.orm.likes import PostLikeOrm, CommentLikeOrm
from infra.orm.posts import PostOrm
from infra.orm.comments import CommentOrm


@dataclass(kw_only=True, slots=True)
class PostLikeDm(IPostLikeDm):
    _tm: TransactionManager

    async def lock_post(self, *, post_id: int) -> bool:
        query = select(PostOrm.id).where(PostOrm.id == post_id).with_for_update()

        return await self._tm.scalar(statement=query) is not None

    async def exists(self, *, user_id: int, post_id: int) -> bool:
        like = await self._tm.get(
            entity=PostLikeOrm,
            identifier=(user_id, post_id),
        )

        return like is not None

    async def create(self, *, user_id: int, post_id: int) -> None:
        like = PostLikeOrm(user_id=user_id, post_id=post_id)

        self._tm.add(instance=like)
        await self._tm.flush(instances=[like])

    async def delete(self, *, user_id: int, post_id: int) -> None:
        like = await self._tm.get(
            entity=PostLikeOrm,
            identifier=(user_id, post_id),
        )
        if like is None:
            return

        await self._tm.delete(instance=like)
        await self._tm.flush()


@dataclass(kw_only=True, slots=True)
class CommentLikeDm(ICommentLikeDm):
    _tm: TransactionManager

    async def lock_comment(self, *, comment_id: int) -> bool:
        query = select(CommentOrm.id).where(CommentOrm.id == comment_id).with_for_update()

        return await self._tm.scalar(statement=query) is not None

    async def exists(self, *, user_id: int, comment_id: int) -> bool:
        like = await self._tm.get(
            entity=CommentLikeOrm,
            identifier=(user_id, comment_id),
        )

        return like is not None

    async def create(self, *, user_id: int, comment_id: int) -> None:
        like = CommentLikeOrm(user_id=user_id, comment_id=comment_id)

        self._tm.add(instance=like)
        await self._tm.flush(instances=[like])

    async def delete(self, *, user_id: int, comment_id: int) -> None:
        like = await self._tm.get(
            entity=CommentLikeOrm,
            identifier=(user_id, comment_id),
        )
        if like is None:
            return

        await self._tm.delete(instance=like)
        await self._tm.flush()
