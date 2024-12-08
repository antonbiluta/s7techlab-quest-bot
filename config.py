import asyncio
import re

import aiohttp

from spring_centralized_config_client.client import SpringCentralizedConfigClient


class ConfigManager:
    def __init__(self,
                 config_server_url: str = "http://config-server.biluta-tech.svc.cluster.local:8888",
                 app_name: str = "s7quest",
                 profile: str = "default"):
        self.client = SpringCentralizedConfigClient(app_name=app_name, profile=profile, url=config_server_url)
        self.config_server_url = config_server_url
        self.app_name = app_name
        self.profile = profile
        self.config = {}
        self.source_config = {}
        self.listeners = []

    async def load_config(self):
        self.source_config = self.client.get_config()
        self.config = unflatten_dict(self.source_config)

    async def refresh_config(self):
        url = f"{self.config_server_url}/actuator/refresh"
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                if response.status == 200:
                    changes = await response.json()
                    if changes:
                        await self.load_config()

    def add_listener(self, callback):
        self.listeners.append(callback)

    async def notify_listeners(self):
        for listener in self.listeners:
            if asyncio.iscoroutinefunction(listener):
                await listener(self.config)
            else:
                listener(self.config)

    async def start_auto_refresh(self, interval: int = 60):
        while True:
            await self.refresh_config()
            await asyncio.sleep(interval)


BOT_TOKEN = ""
ALLOWED_ADMINS = list()
ADMIN_GROUP_ID = 0
TEAMS_INFO = dict()


def unflatten_dict(flat_dict, delimiter='.', list_pattern=r'\[(\d+)\]'):
    """
    Преобразует плоский словарь в иерархический (вложенные словари и списки).
    :param flat_dict: Плоский словарь с ключами в точечной нотации.
    :param delimiter: Разделитель между уровнями (по умолчанию ".").
    :param list_pattern: Шаблон для распознавания массивов (например, [0], [1]).
    :return: Вложенный словарь/список.
    """
    nested_dict = {}
    list_regex = re.compile(list_pattern)

    for key, value in flat_dict.items():
        keys = key.split(delimiter)
        current_level = nested_dict

        for i, part in enumerate(keys):
            match = list_regex.search(part)
            if match:
                array_key = part[:match.start()]
                index = int(match.group(1))
                if array_key not in current_level:
                    current_level[array_key] = []
                while len(current_level[array_key]) <= index:
                    current_level[array_key].append({})
                if i == len(keys) - 1:
                    current_level[array_key][index] = value
                else:
                    current_level = current_level[array_key][index]
            else:
                if i == len(keys) - 1:
                    current_level[part] = value
                else:
                    current_level = current_level.setdefault(part, {})

    return nested_dict


async def update_globals(config):
    global BOT_TOKEN, ALLOWED_ADMINS, ADMIN_GROUP_ID, TEAMS_INFO

    config = unflatten_dict(config)
    print(config)
    bot = config["bot"]
    quest = config["quest"]
    BOT_TOKEN = bot.get('token', "")
    ALLOWED_ADMINS = bot['parameters'].get('allowed_admins', list())
    ADMIN_GROUP_ID = bot["parameters"].get("admin_group_id", list())
    TEAMS_INFO = quest["parameters"].get("teams_info", dict())

    print("Глобальные переменные обновлены:")
    print(f"BOT_TOKEN: {BOT_TOKEN}")
    print(f"ALLOWED_ADMINS: {ALLOWED_ADMINS}")
    print(f"ADMIN_GROUP_ID: {ADMIN_GROUP_ID}")
    print(f"TEAMS_INFO: {TEAMS_INFO}")
