"""
文件路径: /backend/app/user/services/async_user.py
功能描述: 用户异步业务服务
主要功能:
    - 用户 CRUD 业务封装
    - 用户认证逻辑
    - 密码验证与处理
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.crud import async_user as user_crud
from app.user.models.user import User
from app.user.schemas.auth import PasswordChangeRequest, SelfProfileUpdate
from app.user.schemas.user_in import UserCreate, UserPasswordReset, UserUpdate
from common.error_codes import ErrorCode
from common.exceptions import BusinessException
from core.security import hash_password, validate_password, verify_password


class UserService:
    """用户服务"""

    MANAGED_ROLES = {"supervisor", "operator"}

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> User | None:
        """根据用户名获取用户"""
        return await user_crud.get_by_username(db, username)

    @staticmethod
    async def get_all(db: AsyncSession) -> list[User]:
        """获取所有用户"""
        return await user_crud.get_all(db)

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page: int,
        page_size: int,
        username: str | None = None,
        role: str | None = None,
    ) -> tuple[list[User], int]:
        """分页查询用户"""
        return await user_crud.get_page(db, page, page_size, username, role)

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
        """根据 ID 获取用户"""
        return await user_crud.get_by_id(db, user_id)

    @staticmethod
    async def create(
        db: AsyncSession,
        user_data: UserCreate,
        *,
        actor: User,
    ) -> User:
        """创建用户"""
        explicit_role = "role" in user_data.model_fields_set

        if actor.role == "supervisor" and (explicit_role and user_data.role != "operator"):
            raise BusinessException(ErrorCode.CANNOT_MANAGE_USER_ROLE, code=403)

        if actor.role not in {"admin", "supervisor"}:
            raise BusinessException(ErrorCode.TARGET_USER_NOT_MANAGEABLE, code=403)

        if user_data.role == "admin":
            raise BusinessException(ErrorCode.CANNOT_CREATE_ADMIN, code=403)

        if actor.role == "admin" and user_data.role not in UserService.MANAGED_ROLES:
            raise BusinessException(ErrorCode.CANNOT_MANAGE_USER_ROLE, code=403)

        existing = await UserService.get_by_username(db, user_data.username)
        if existing:
            raise BusinessException(ErrorCode.USERNAME_ALREADY_EXISTS)

        is_valid, error_msg = validate_password(user_data.password)
        if not is_valid:
            raise BusinessException(ErrorCode.INVALID_PASSWORD_POLICY, message=error_msg)

        user = User(
            username=user_data.username,
            password=hash_password(user_data.password),
            name=user_data.name,
            role=user_data.role,
            phone=user_data.phone,
            email=user_data.email,
        )
        return await user_crud.create(db, user)

    @staticmethod
    async def update(
        db: AsyncSession,
        user_id: int,
        user_data: UserUpdate,
        *,
        actor: User,
    ) -> User | None:
        """更新用户"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        update_data = UserService._normalize_user_update(update_data)

        if user.id == actor.id:
            UserService._ensure_self_management_update_allowed(update_data)

        if "role" in update_data and actor.role != "admin":
            raise BusinessException(ErrorCode.CANNOT_MANAGE_USER_ROLE, code=403)

        if user.id != actor.id:
            UserService._ensure_can_manage_target(actor, user)

        if user.role == "admin" and actor.role != "admin":
            raise BusinessException(ErrorCode.CANNOT_DISABLE_ADMIN, code=403)

        if user.role == "admin" and (
            "is_active" in update_data
            or update_data.get("role") not in {None, "admin"}
        ):
            raise BusinessException(ErrorCode.CANNOT_DISABLE_ADMIN, code=403)

        if user.role != "admin" and update_data.get("role") == "admin":
            raise BusinessException(ErrorCode.CANNOT_CREATE_ADMIN, code=403)

        if "role" in update_data and update_data["role"] not in UserService.MANAGED_ROLES:
            raise BusinessException(ErrorCode.CANNOT_MANAGE_USER_ROLE, code=403)

        return await user_crud.update(db, user, update_data)

    @staticmethod
    async def delete(db: AsyncSession, user_id: int, *, actor: User) -> bool:
        """删除用户（软删除）"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return False

        if user.id == actor.id:
            raise BusinessException(ErrorCode.CANNOT_DELETE_SELF, code=403)

        if user.role == "admin":
            raise BusinessException(ErrorCode.CANNOT_DELETE_ADMIN, code=403)

        UserService._ensure_can_manage_target(actor, user)

        await user_crud.soft_delete(db, user)
        return True

    @staticmethod
    async def update_self_profile(
        db: AsyncSession,
        actor: User,
        profile_data: SelfProfileUpdate,
    ) -> User:
        """更新当前登录用户自己的基础资料。"""
        update_data = profile_data.model_dump(exclude_unset=True)
        return await user_crud.update(db, actor, update_data)

    @staticmethod
    async def change_own_password(
        db: AsyncSession,
        actor: User,
        password_data: PasswordChangeRequest,
    ) -> dict:
        """当前登录用户修改自己的密码。"""
        if not password_data.old_password:
            raise BusinessException(ErrorCode.OLD_PASSWORD_REQUIRED, code=400)

        if not verify_password(password_data.old_password, actor.password):
            raise BusinessException(ErrorCode.OLD_PASSWORD_INCORRECT, code=400)

        UserService._validate_new_password(password_data.new_password)
        await user_crud.update(db, actor, {"password": hash_password(password_data.new_password)})
        return {"requires_relogin": True}

    @staticmethod
    async def reset_password(
        db: AsyncSession,
        user_id: int,
        password_data: UserPasswordReset,
        *,
        actor: User,
    ) -> dict | None:
        """管理者重置目标用户密码。"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return None

        if user.id == actor.id:
            raise BusinessException(ErrorCode.CANNOT_OPERATE_SELF, code=403)

        if user.role == "admin":
            raise BusinessException(ErrorCode.TARGET_USER_NOT_MANAGEABLE, code=403)

        UserService._ensure_can_manage_target(actor, user)
        UserService._validate_new_password(password_data.new_password)
        await user_crud.update(db, user, {"password": hash_password(password_data.new_password)})
        return {"requires_relogin": True}

    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> User | None:
        """认证用户"""
        user = await UserService.get_by_username(db, username)
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    @staticmethod
    def _normalize_user_update(update_data: dict) -> dict:
        if "status" in update_data:
            status = update_data.pop("status")
            update_data["is_active"] = status == "active"
        return update_data

    @staticmethod
    def _ensure_self_management_update_allowed(update_data: dict) -> None:
        restricted_fields = {"role", "is_active"}
        if restricted_fields.intersection(update_data):
            raise BusinessException(ErrorCode.CANNOT_OPERATE_SELF, code=403)

    @staticmethod
    def _ensure_can_manage_target(actor: User, target: User) -> None:
        if actor.role == "admin":
            if target.role == "admin":
                raise BusinessException(ErrorCode.TARGET_USER_NOT_MANAGEABLE, code=403)
            return

        if actor.role == "supervisor" and target.role == "operator":
            return

        raise BusinessException(ErrorCode.TARGET_USER_NOT_MANAGEABLE, code=403)

    @staticmethod
    def _validate_new_password(new_password: str | None) -> None:
        if not new_password:
            raise BusinessException(ErrorCode.INVALID_PASSWORD_POLICY)

        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            raise BusinessException(ErrorCode.INVALID_PASSWORD_POLICY, message=error_msg)
