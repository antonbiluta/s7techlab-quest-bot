from typing import List

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.base import with_session
from data.models.team import TeamChat


@with_session
async def get_team(session: AsyncSession, team_id: int) -> TeamChat:
    result = await session.execute(select(TeamChat).where(TeamChat.group_id == team_id))
    return result.scalars().first()


@with_session
async def get_team_with_users(session: AsyncSession, team_id: int):
    team = await get_team(team_id)
    if team:
        await session.refresh(team)
    return team


@with_session
async def are_all_chats_full(session: AsyncSession) -> bool:
    result = await session.execute(select(TeamChat.id).where(TeamChat.current_number != TeamChat.member_limit))
    return result.first() is None


@with_session
async def update_members(session: AsyncSession, team_id: int, increment: int):
    stmt = (
        update(TeamChat)
        .where(TeamChat.group_id == team_id)
        .values(current_number=TeamChat.current_number + increment)
    )
    await session.execute(stmt)


@with_session
async def get_team_by_name(session: AsyncSession, team_name):
    result = await session.execute(select(TeamChat).where(TeamChat.name == team_name))
    team = result.scalars().first()
    if team:
        await session.refresh(team)
    return team


@with_session
async def init_teams_from_config(session: AsyncSession, config: dict, default_on: bool):
    quest_parameters = config["quest"]["parameters"]
    default_limit = quest_parameters.get("default_limit", 1)
    teams_info = quest_parameters.get("teams_info", dict())

    for team_code, values in teams_info.items():
        result = await session.execute(select(TeamChat).where(TeamChat.name == team_code))
        existing_team = result.scalars().first()
        if existing_team:
            if default_on:
                existing_team.member_limit = default_limit
            continue
        team = TeamChat(
            group_id=values['chat_id'],
            name=team_code,
            invite_link=values['link'],
            member_limit=default_limit
        )
        session.add(team)

    await session.commit()


@with_session
async def get_all_teams(session: AsyncSession) -> List[TeamChat]:
    result = await session.execute(select(TeamChat))
    return result.scalars().all()


@with_session
async def update_limit_by_name(session: AsyncSession, team_name: str, limit: int):
    stmt = (
        update(TeamChat)
        .where(TeamChat.name == team_name)
        .values(member_limit=limit)
    )
    await session.execute(stmt)


@with_session
async def update_invite_link_by_name(session: AsyncSession, team_name: str, invite_link: str):
    stmt = (
        update(TeamChat)
        .where(TeamChat.name == team_name)
        .values(invite_link=invite_link)
    )
    await session.execute(stmt)

