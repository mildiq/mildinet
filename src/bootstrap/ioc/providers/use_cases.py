from datetime import timedelta

from dishka import Provider, Scope, provide

from application.interfaces.clock import IClock
from application.interfaces.dm import (
    IPostLikeDm,
    IMessageDm,
    IPostDm,
    IRefreshSessionDm,
    IUserDm,
    ICommentDm,
)
from application.interfaces.dm.likes import ICommentLikeDm
from application.interfaces.dm.media import IMediaDm
from application.interfaces.dm.stored_object import IStoredObjectDm
from application.interfaces.security import IPasswordHasher, ITokenService
from application.interfaces.storage import IFileStorage
from application.interfaces.transaction import ITransactionManager
from application.use_cases.auth import (
    AuthenticateUc,
    LoginUc,
    LogoutUc,
    RefreshTokensUc,
    RegisterUserUc,
)
from application.use_cases.comments import (
    ListCommentsUc,
    CreateCommentUc,
    UpdateCommentUc,
    DeleteCommentUc,
    ToggleCommentLikeUc
)
from application.use_cases.media import DownloadMediaUc, ListMediaUc
from application.use_cases.media.delete import DeleteMediaUc
from application.use_cases.media.get import GetMediaUc
from application.use_cases.media.upload import UploadMediaRs, UploadMediaUc
from application.use_cases.messages import ListMessagesUc, SendMessageUc
from application.use_cases.posts import (
    CreatePostUc,
    DeletePostUc,
    ListPostsUc,
    TogglePostLikeUc,
    UpdatePostUc,
)
from application.use_cases.users import GetUserUc, ListUsersUc
from bootstrap.settings import Settings


class UseCaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def register_user(
        self,
        *,
        users: IUserDm,
        passwords: IPasswordHasher,
        transaction: ITransactionManager,
    ) -> RegisterUserUc:
        return RegisterUserUc(
            _users=users,
            _passwords=passwords,
            _transaction=transaction,
        )

    @provide(scope=Scope.REQUEST)
    def login(
        self,
        *,
        users: IUserDm,
        sessions: IRefreshSessionDm,
        passwords: IPasswordHasher,
        tokens: ITokenService,
        clock: IClock,
        transaction: ITransactionManager,
        settings: Settings,
    ) -> LoginUc:
        return LoginUc(
            _users=users,
            _sessions=sessions,
            _passwords=passwords,
            _tokens=tokens,
            _clock=clock,
            _transaction=transaction,
            _refresh_ttl=timedelta(days=settings.refresh_token_ttl_days),
        )

    @provide(scope=Scope.REQUEST)
    def refresh_tokens(
            self,
            *,
            sessions: IRefreshSessionDm,
            users: IUserDm,
            tokens: ITokenService,
            clock: IClock,
            transaction: ITransactionManager,
            settings: Settings,
    ) -> RefreshTokensUc:
        return RefreshTokensUc(
            _sessions=sessions,
            _users=users,
            _tokens=tokens,
            _clock=clock,
            _transaction=transaction,
            _refresh_ttl=timedelta(days=settings.refresh_token_ttl_days),
        )

    @provide(scope=Scope.REQUEST)
    def logout(
            self,
            *,
            sessions: IRefreshSessionDm,
            tokens: ITokenService,
            clock: IClock,
            transaction: ITransactionManager,
    ) -> LogoutUc:
        return LogoutUc(
            _sessions=sessions,
            _tokens=tokens,
            _clock=clock,
            _transaction=transaction,
        )

    @provide(scope=Scope.REQUEST)
    def authenticate(
            self,
            *,
            users: IUserDm,
            tokens: ITokenService,
    ) -> AuthenticateUc:
        return AuthenticateUc(_users=users, _tokens=tokens)

    @provide(scope=Scope.REQUEST)
    def get_user(self, *, users: IUserDm) -> GetUserUc:
        return GetUserUc(_users=users)

    @provide(scope=Scope.REQUEST)
    def list_users(self, *, users: IUserDm) -> ListUsersUc:
        return ListUsersUc(_users=users)

    @provide(scope=Scope.REQUEST)
    def list_posts(self, *, posts: IPostDm) -> ListPostsUc:
        return ListPostsUc(_posts=posts)

    @provide(scope=Scope.REQUEST)
    def create_post(
            self,
            *,
            posts: IPostDm,
            media: IMediaDm,
            transaction: ITransactionManager,
    ) -> CreatePostUc:
        return CreatePostUc(
            _posts=posts,
            _media=media,
            _transaction=transaction,
        )

    @provide(scope=Scope.REQUEST)
    def update_post(
            self,
            *,
            posts: IPostDm,
            transaction: ITransactionManager,
    ) -> UpdatePostUc:
        return UpdatePostUc(_posts=posts, _transaction=transaction)

    @provide(scope=Scope.REQUEST)
    def delete_post(
            self,
            *,
            posts: IPostDm,
            transaction: ITransactionManager,
    ) -> DeletePostUc:
        return DeletePostUc(_posts=posts, _transaction=transaction)

    @provide(scope=Scope.REQUEST)
    def toggle_post_like(
            self,
            *,
            posts: IPostDm,
            likes: IPostLikeDm,
            transaction: ITransactionManager,
    ) -> TogglePostLikeUc:
        return TogglePostLikeUc(
            _posts=posts,
            _likes=likes,
            _transaction=transaction,
        )

    @provide(scope=Scope.REQUEST)
    def list_comments(self, *, comments: ICommentDm) -> ListCommentsUc:
        return ListCommentsUc(_comments=comments)

    @provide(scope=Scope.REQUEST)
    def create_comment(
            self,
            *,
            comments: ICommentDm,
            transaction: ITransactionManager,
    ) -> CreateCommentUc:
        return CreateCommentUc(_comments=comments, _transaction=transaction)

    @provide(scope=Scope.REQUEST)
    def update_comment(
            self,
            *,
            comments: ICommentDm,
            transaction: ITransactionManager,
    ) -> UpdateCommentUc:
        return UpdateCommentUc(_comments=comments, _transaction=transaction)

    @provide(scope=Scope.REQUEST)
    def delete_comment(
            self,
            *,
            comments: ICommentDm,
            transaction: ITransactionManager,
    ) -> DeleteCommentUc:
        return DeleteCommentUc(_comments=comments, _transaction=transaction)

    @provide(scope=Scope.REQUEST)
    def toggle_comment_like(
            self,
            *,
            comments: ICommentDm,
            likes: ICommentLikeDm,
            transaction: ITransactionManager,
    ) -> ToggleCommentLikeUc:
        return ToggleCommentLikeUc(
            _comments=comments,
            _likes=likes,
            _transaction=transaction,
        )

    @provide(scope=Scope.REQUEST)
    def list_messages(
            self,
            *,
            messages: IMessageDm,
            users: IUserDm,
    ) -> ListMessagesUc:
        return ListMessagesUc(_messages=messages, _users=users)

    @provide(scope=Scope.REQUEST)
    def send_message(
            self,
            *,
            messages: IMessageDm,
            users: IUserDm,
            transaction: ITransactionManager,
    ) -> SendMessageUc:
        return SendMessageUc(
            _messages=messages,
            _users=users,
            _transaction=transaction,
        )

    @provide(scope=Scope.REQUEST)
    def upload_media(
        self,
        *,
        storage: IFileStorage,
        media: IMediaDm,
        transaction: ITransactionManager,
        settings: Settings,
        stored_object: IStoredObjectDm
    ) -> UploadMediaUc:
        return UploadMediaUc(
            _storage=storage,
            _media=media,
            _transaction=transaction,
            _settings=settings,
            _stored_object=stored_object,
        )

    @provide(scope=Scope.REQUEST)
    def get_media(
        self,
        *,
        media: IMediaDm,
    ) -> GetMediaUc:
        return GetMediaUc(_media=media)

    @provide(scope=Scope.REQUEST)
    def download_media(
        self,
        *,
        media: IMediaDm,
        storage: IFileStorage,
    ) -> DownloadMediaUc:
        return DownloadMediaUc(
            _media=media,
            _storage=storage,
        )

    @provide(scope=Scope.REQUEST)
    def delete_media(
            self,
            *,
            media: IMediaDm,
            stored: IStoredObjectDm,
            storage: IFileStorage,
            transaction: ITransactionManager,
    ) -> DeleteMediaUc:
        return DeleteMediaUc(
            _media=media,
            _stored_object=stored,
            _storage=storage,
            _transaction=transaction,
        )

    @provide(scope=Scope.REQUEST)
    def list_media(
            self,
            *,
            media: IMediaDm,
    ) -> ListMediaUc:
        return ListMediaUc(
            _media=media,
        )