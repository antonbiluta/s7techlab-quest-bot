from contextlib import asynccontextmanager
from functools import wraps
from inspect import signature

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base


Base = declarative_base()


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.async_session = None

    def init_engine(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=True)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self):
        if self.engine is None:
            raise RuntimeError("Engine не инициализирован")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session_scope(self):
        if self.async_session is None:
            raise RuntimeError('You must call init_db_engine() before calling get_session()')
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


db_manager = DatabaseManager()


def with_session(func):
    """
    Декоратор для автоматического управления сессией.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        func_sig = signature(func)
        parameters = func_sig.parameters
        session_arg_position = list(parameters).index("session") if "session" in parameters else None
        if session_arg_position is not None and len(args) > session_arg_position:
            session = args[session_arg_position]
            if isinstance(session, AsyncSession):
                return await func(*args, **kwargs)
        async with db_manager.session_scope() as session:
            return await func(session, *args, **kwargs)
    return wrapper
