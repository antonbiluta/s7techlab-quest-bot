from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.base import with_session
from data.models.settings import Settings


@with_session
async def create_settings(session: AsyncSession, name: str, is_work: bool = False, params: str = None):
    exists = await get_settings_by_name(session, name)
    if exists:
        return
    settings = Settings(name=name, is_work=is_work, params=params)
    session.add(settings)
    await session.commit()


@with_session
async def get_settings_by_name(session: AsyncSession, name: str) -> Settings:
    result = await session.execute(select(Settings).where(Settings.name == name))
    return result.scalars().first()
