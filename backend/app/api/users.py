"""User management endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import AdminUser, CurrentActiveUser, DB
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user: CurrentActiveUser) -> UserResponse:
    """Get current user's profile."""
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    update_data: UserUpdate,
    user: CurrentActiveUser,
    db: DB,
) -> UserResponse:
    """Update current user's profile."""
    if update_data.email is not None:
        # Check if email is taken
        stmt = select(User).where(
            User.email == update_data.email,
            User.id != user.id,
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use",
            )
        user.email = update_data.email

    if update_data.full_name is not None:
        user.full_name = update_data.full_name

    if update_data.password is not None:
        user.hashed_password = hash_password(update_data.password)

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.get("", response_model=list[UserResponse])
async def list_users(
    admin: AdminUser,
    db: DB,
    skip: int = 0,
    limit: int = 100,
) -> list[UserResponse]:
    """List all users (admin only).

    Results are scoped to the admin's tenant.
    """
    stmt = (
        select(User)
        .where(User.tenant_id == admin.tenant_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    users = result.scalars().all()

    return [UserResponse.model_validate(u) for u in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    admin: AdminUser,
    db: DB,
) -> UserResponse:
    """Get a specific user (admin only)."""
    stmt = select(User).where(
        User.id == user_id,
        User.tenant_id == admin.tenant_id,
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    admin: AdminUser,
    db: DB,
) -> UserResponse:
    """Create a new user (admin only)."""
    # Check if email exists in tenant
    stmt = select(User).where(
        User.email == user_data.email,
        User.tenant_id == admin.tenant_id,
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        tenant_id=admin.tenant_id,
        roles=["user"],
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    update_data: UserUpdate,
    admin: AdminUser,
    db: DB,
) -> UserResponse:
    """Update a user (admin only)."""
    stmt = select(User).where(
        User.id == user_id,
        User.tenant_id == admin.tenant_id,
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if update_data.email is not None:
        # Check if email is taken
        stmt = select(User).where(
            User.email == update_data.email,
            User.id != user_id,
            User.tenant_id == admin.tenant_id,
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use",
            )
        user.email = update_data.email

    if update_data.full_name is not None:
        user.full_name = update_data.full_name

    if update_data.password is not None:
        user.hashed_password = hash_password(update_data.password)

    if update_data.is_active is not None:
        user.is_active = update_data.is_active

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    admin: AdminUser,
    db: DB,
) -> None:
    """Delete a user (admin only).

    In production, consider soft delete instead.
    """
    stmt = select(User).where(
        User.id == user_id,
        User.tenant_id == admin.tenant_id,
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent self-deletion
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    await db.delete(user)
    await db.commit()
