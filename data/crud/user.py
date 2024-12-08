from typing import Any, Sequence

from sqlalchemy import Row, RowMapping
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from data.base import with_session
from data.models.user import User


@with_session
async def create_user(session: AsyncSession, user_id: int, username: str, team_id: int = None):
    user = User(id=user_id, username=username, team_id=team_id)
    session.add(user)
    await session.commit()
    await session.refresh(user)


@with_session
async def create_or_update_user(session: AsyncSession, user_id: int, username: str, team_id: int = None):
    user = await get_user(session, user_id)
    if not user:
        await create_user(session, user_id, username, team_id)
        return
    user.team_id = team_id
    await session.commit()
    await session.refresh(user)


@with_session
async def get_user(session: AsyncSession, user_id: int) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


@with_session
async def get_user_team(session: AsyncSession, user_id: int) -> int:
    result = await session.execute(select(User.team_id).where(User.id == user_id))
    return result.scalars().first()


@with_session
async def get_user_with_team(session: AsyncSession, user_id: int = None, username: str = None) -> User:
    if user_id:
        result = await session.execute(
            select(User)
            .options(joinedload(User.team))
            .where(User.id == user_id)
        )
        user = result.scalars().first()
        if user:
            return user
    if username:
        result = await session.execute(
            select(User)
            .options(joinedload(User.team))
            .where(User.username == username)
        )
        user = result.scalars().first()
        return user
    return None


@with_session
async def get_user_by_username(session: AsyncSession, username: str) -> User:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalars().first()


@with_session
async def get_users_by_team_id(session: AsyncSession, team_id: int) -> Sequence[Row[Any] | RowMapping | Any]:
    result = await session.execute(select(User).where(User.team_id == team_id))
    return result.scalars().all()


@with_session
async def update_user_team(session: AsyncSession, user_id: int, team_id: int):
    user = await get_user(user_id)
    if not user:
        return None
    user.team_id = team_id
    await session.commit()
    return user


@with_session
async def reset_user_team(session: AsyncSession, user_id: int):
    user = await get_user(session, user_id)
    if not user:
        return None
    user.team_id = None
    await session.commit()
    return user
