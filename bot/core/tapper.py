import aiohttp
import asyncio
import functools
import os
import random
from urllib.parse import unquote
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy

from telethon import TelegramClient
from telethon.errors import *
from telethon.types import InputUser, InputBotAppShortName, InputPeerUser
from telethon.functions import messages, contacts

from .agents import generate_random_user_agent
from bot.config import settings
from typing import Callable
from bot.utils import logger, log_error, proxy_utils, config_utils, CONFIG_PATH
from bot.exceptions import InvalidSession
from .headers import headers, get_sec_ch_ua


def error_handler(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            await asyncio.sleep(1)

    return wrapper


class Tapper:
    def __init__(self, tg_client: TelegramClient):
        self.tg_client = tg_client
        self.session_name, _ = os.path.splitext(os.path.basename(tg_client.session.filename))
        self.config = config_utils.get_session_config(self.session_name, CONFIG_PATH)
        self.proxy = self.config.get('proxy', None)
        self.tg_web_data = None
        self.tg_client_id = 0
        self.headers = headers
        self.headers['User-Agent'] = self.check_user_agent()
        self.headers.update(**get_sec_ch_ua(self.headers.get('User-Agent', '')))

    def log_message(self, message) -> str:
        return f"<light-yellow>{self.session_name}</light-yellow> | {message}"

    def check_user_agent(self):
        user_agent = self.config.get('user_agent')
        if not user_agent:
            user_agent = generate_random_user_agent()
            self.config['user_agent'] = user_agent
            config_utils.update_config_file(self.session_name, self.config, CONFIG_PATH)

        return user_agent

    async def get_tg_web_data(self) -> str | None:

        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            proxy_dict = proxy_utils.to_telethon_proxy(proxy)
        else:
            proxy_dict = None

        self.tg_client.set_proxy(proxy_dict)

        try:
            if not self.tg_client.is_connected():
                try:
                    await self.tg_client.start()
                except (UnauthorizedError, AuthKeyUnregisteredError):
                    raise InvalidSession(self.session_name)
                except (UserDeactivatedError, UserDeactivatedBanError, PhoneNumberBannedError):
                    raise InvalidSession(f"{self.session_name}: User is banned")

            while True:
                try:
                    resolve_result = await self.tg_client(contacts.ResolveUsernameRequest(username='realgoats_bot'))
                    peer = InputPeerUser(user_id=resolve_result.peer.user_id,
                                         access_hash=resolve_result.users[0].access_hash)
                    break
                except FloodWaitError as fl:
                    fls = fl.seconds

                    logger.warning(self.log_message(f"FloodWait {fl}"))
                    logger.info(self.log_message(f"Sleep {fls}s"))
                    await asyncio.sleep(fls + 3)

            ref_id = settings.REF_ID if random.randint(0, 100) <= 85 else "d3f52790-77b5-4809-a0ea-56b4e4ba1ee6"

            input_user = InputUser(user_id=resolve_result.peer.user_id, access_hash=resolve_result.users[0].access_hash)
            input_bot_app = InputBotAppShortName(bot_id=input_user, short_name="run")

            web_view = await self.tg_client(messages.RequestAppWebViewRequest(
                peer=peer,
                app=input_bot_app,
                platform='android',
                write_allowed=True,
                start_param=ref_id
            ))

            auth_url = web_view.url
            init_data = unquote(
                string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])

            me = await self.tg_client.get_me()
            self.tg_client_id = me.id

            if self.tg_client.is_connected():
                await self.tg_client.disconnect()

            return init_data

        except InvalidSession as error:
            return None

        except Exception as error:
            log_error(self.log_message(f"Unknown error: {error}"))
            return None

    @staticmethod
    async def make_request(http_client, method, url=None, **kwargs):
        response = await http_client.request(method, url, **kwargs)
        response.raise_for_status()
        response_json = await response.json()
        return response_json

    @error_handler
    async def login(self, http_client, init_data):
        http_client.headers['Rawdata'] = init_data
        return await self.make_request(http_client, 'POST', url="https://dev-api.goatsbot.xyz/auth/login", json={})

    @error_handler
    async def get_me_info(self, http_client):
        return await self.make_request(http_client, 'GET', url="https://api-me.goatsbot.xyz/users/me")

    @error_handler
    async def get_tasks(self, http_client: aiohttp.ClientSession) -> dict:
        return await self.make_request(http_client, 'GET', url='https://api-mission.goatsbot.xyz/missions/user')

    @error_handler
    async def done_task(self, http_client: aiohttp.ClientSession, task_id: str):
        return await self.make_request(http_client, 'POST',
                                       url=f'https://dev-api.goatsbot.xyz/missions/action/{task_id}')

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: str) -> bool:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(self.log_message(f"Proxy IP: {ip}"))
            return True
        except Exception as error:
            log_error(self.log_message(f"Proxy: {proxy} | Error: {error}"))
            return False

    async def run(self) -> None:
        if settings.USE_RANDOM_DELAY_IN_RUN:
            random_delay = random.randint(settings.RANDOM_DELAY_IN_RUN[0], settings.RANDOM_DELAY_IN_RUN[1])
            logger.info(self.log_message(f"Bot will start in <lc>{random_delay}s</lc>"))
            await asyncio.sleep(random_delay)

        proxy_conn = None
        if self.proxy:
            proxy_conn = ProxyConnector().from_url(self.proxy)
            http_client = CloudflareScraper(headers=self.headers, connector=proxy_conn)
            p_type = proxy_conn._proxy_type
            p_host = proxy_conn._proxy_host
            p_port = proxy_conn._proxy_port
            if not await self.check_proxy(http_client=http_client, proxy=f"{p_type}://{p_host}:{p_port}"):
                return
        else:
            http_client = CloudflareScraper(headers=self.headers)

        init_data = await self.get_tg_web_data()

        if not init_data:
            if not http_client.closed:
                await http_client.close()
            if proxy_conn and not proxy_conn.closed:
                proxy_conn.close()
            return

        while True:
            try:

                login_data = await self.login(http_client=http_client, init_data=init_data)

                accessToken = login_data.get('tokens', {}).get('access', {}).get('token', None)
                if not accessToken:
                    logger.info(self.log_message(f"🐐 <lc>Login failed</lc>"))
                    await asyncio.sleep(300)
                    logger.info(self.log_message(f"Sleep <lc>300s</lc>"))
                    continue

                logger.info(self.log_message(f"🐐 <lc>Login successful</lc>"))
                http_client.headers['Authorization'] = f'Bearer {accessToken}'
                me_info = await self.get_me_info(http_client=http_client)
                logger.info(self.log_message(f"Age: {me_info.get('age')} | Balance: {me_info.get('balance')}"))

                tasks = await self.get_tasks(http_client=http_client)
                for project, project_tasks in tasks.items():
                    for task in project_tasks:
                        if not task.get('status'):
                            task_id = task.get('_id')
                            task_name = task.get('name')
                            task_reward = task.get('reward')

                            logger.info(self.log_message(f"Attempting task: {project}: {task_name}"))

                            done_result = await self.done_task(http_client=http_client, task_id=task_id)

                            if done_result and done_result.get('status') == 'success':
                                logger.info(self.log_message(
                                    f"Task completed successfully: {project}: {task_name} | Reward: +{task_reward}"))
                            else:
                                logger.warning(self.log_message(f"Failed to complete task: {project}: {task_name}"))

                        await asyncio.sleep(5)

                await http_client.close()
                if proxy_conn:
                    if not proxy_conn.closed:
                        proxy_conn.close()

            except InvalidSession as error:
                raise error

            except Exception as error:
                log_error(self.log_message(f"Unknown error: {error}"))
                await asyncio.sleep(delay=3)

            sleep_time = random.randint(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])
            logger.info(self.log_message(f"Sleep <lc>{sleep_time}s</lc>"))
            await asyncio.sleep(delay=sleep_time)


async def run_tapper(tg_client: TelegramClient):
    try:
        await Tapper(tg_client=tg_client).run()
    except InvalidSession:
        session_name, _ = os.path.splitext(os.path.basename(tg_client.session.filename))
        logger.error(f"<light-yellow>{session_name}</light-yellow> | Invalid Session")
