import aiohttp
import asyncio
import functools
import json
import random
import re
from urllib.parse import unquote, parse_qs
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from random import uniform, randint
from time import time

from bot.utils.universal_telegram_client import UniversalTelegramClient

from bot.config import settings
from typing import Callable
from bot.utils import logger, log_error, config_utils, date_utils, CONFIG_PATH, first_run
from bot.exceptions import InvalidSession
from .headers import headers, get_sec_ch_ua


def error_handler(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        retries = 2
        while retries >= 0:
            try:
                return await func(*args, **kwargs)
            except (asyncio.exceptions.TimeoutError, aiohttp.ServerDisconnectedError,
                    aiohttp.ClientProxyConnectionError) as e:
                if retries > 0:
                    log_error(f"Error: {type(e).__name__}. Retrying")
                    retries -= 1
                    await asyncio.sleep(1)
                else:
                    raise
            except Exception as e:
                await asyncio.sleep(1)
    return wrapper


class Tapper:
    def __init__(self, tg_client: UniversalTelegramClient):
        self.tg_client = tg_client
        self.session_name = tg_client.session_name

        session_config = config_utils.get_session_config(self.session_name, CONFIG_PATH)

        if not all(key in session_config for key in ('api', 'user_agent')):
            logger.critical(self.log_message('CHECK accounts_config.json as it might be corrupted'))
            exit(-1)

        self.headers = headers
        user_agent = session_config.get('user_agent')
        self.headers['user-agent'] = user_agent
        self.headers.update(**get_sec_ch_ua(user_agent))

        self.proxy = session_config.get('proxy')
        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            self.tg_client.set_proxy(proxy)

        self.tg_web_data = None
        self.tg_client_id = 0

        self._webview_data = None

    def log_message(self, message) -> str:
        return f"<ly>{self.session_name}</ly> | {message}"

    async def get_tg_web_data(self) -> str:
        webview_url = await self.tg_client.get_app_webview_url('realgoats_bot', "run", "d3f52790-77b5-4809-a0ea-56b4e4ba1ee6")

        tg_web_data = unquote(string=webview_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
        user_data = json.loads(parse_qs(tg_web_data).get('user', [''])[0])

        self.tg_client_id = user_data.get('id')

        return tg_web_data

    @staticmethod
    async def make_request(http_client: CloudflareScraper, method, url=None, **kwargs):
        response = await http_client.request(method, url, **kwargs)
        response.raise_for_status()
        response_json = await response.json()
        return response_json

    @error_handler
    async def login(self, http_client: CloudflareScraper, init_data):
        http_client.headers['Rawdata'] = init_data
        return await self.make_request(http_client, 'POST', url="https://dev-api.goatsbot.xyz/auth/login", json={})

    @error_handler
    async def get_me_info(self, http_client: CloudflareScraper):
        return await self.make_request(http_client, 'GET', url="https://api-me.goatsbot.xyz/users/me")

    @error_handler
    async def get_tasks(self, http_client: CloudflareScraper) -> dict:
        return await self.make_request(http_client, 'GET', url='https://api-mission.goatsbot.xyz/missions/user')

    @error_handler
    async def done_task(self, http_client: CloudflareScraper, task_id: str):
        return await self.make_request(http_client, 'POST',
                                       url=f'https://dev-api.goatsbot.xyz/missions/action/{task_id}')

    @error_handler
    async def get_checkin_options(self, http_client: CloudflareScraper):
        return await self.make_request(http_client, 'GET', url="https://api-checkin.goatsbot.xyz/checkin/user")

    @error_handler
    async def perform_checkin(self, http_client: CloudflareScraper, checkin_id: str):
        return await self.make_request(http_client, 'POST',
                                       url=f'https://api-checkin.goatsbot.xyz/checkin/action/{checkin_id}')

    async def check_proxy(self, http_client: CloudflareScraper) -> bool:
        proxy_conn = http_client.connector
        if proxy_conn and not hasattr(proxy_conn, '_proxy_host'):
            logger.info(self.log_message(f"Running Proxy-less"))
            return True
        try:
            response = await http_client.get(url='https://ifconfig.me/ip', timeout=aiohttp.ClientTimeout(15))
            logger.info(self.log_message(f"Proxy IP: {await response.text()}"))
            return True
        except Exception as error:
            proxy_url = f"{proxy_conn._proxy_type}://{proxy_conn._proxy_host}:{proxy_conn._proxy_port}"
            log_error(self.log_message(f"Proxy: {proxy_url} | Error: {type(error).__name__}"))
            return False

    async def run(self) -> None:
        if settings.USE_RANDOM_DELAY_IN_RUN:
            random_delay = random.uniform(settings.RANDOM_DELAY_IN_RUN[0], settings.RANDOM_DELAY_IN_RUN[1])
            logger.info(self.log_message(f"Bot will start in <lc>{int(random_delay)}s</lc>"))
            await asyncio.sleep(random_delay)

        access_token_created_time = 0
        init_data = None

        token_live_time = random.randint(3500, 3600)

        proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
        async with CloudflareScraper(headers=self.headers, timeout=aiohttp.ClientTimeout(60), **proxy_conn) as http_client:
            while True:
                if not await self.check_proxy(http_client=http_client):
                    logger.warning(self.log_message('Failed to connect to proxy server. Sleep 5 minutes.'))
                    await asyncio.sleep(300)
                    continue

                try:
                    if time() - access_token_created_time >= token_live_time:
                        init_data = await self.get_tg_web_data()

                        if not init_data:
                            logger.warning(self.log_message('Failed to get webview URL'))
                            await asyncio.sleep(300)
                            continue

                    access_token_created_time = time()

                    login_data = await self.login(http_client=http_client, init_data=init_data)

                    access_token = login_data.get('tokens', {}).get('access', {}).get('token', None)
                    if not access_token:
                        logger.info(self.log_message(f"🐐 <lc>Login failed</lc>"))
                        await asyncio.sleep(300)
                        logger.info(self.log_message(f"Sleep <lc>300s</lc>"))
                        continue

                    logger.info(self.log_message(f"🐐 <lc>Login successful</lc>"))
                    if self.tg_client.is_fist_run:
                        await first_run.append_recurring_session(self.session_name)
                    http_client.headers['Authorization'] = f'Bearer {access_token}'
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

                    checkin = await self.get_checkin_options(http_client=http_client)
                    last_checkin = checkin.get('lastCheckinTime')
                    if checkin and last_checkin is not None:
                        for day in checkin.get('result', []):
                            if (last_checkin == 0 or date_utils.is_next_day(last_checkin)) and day.get('status') is False:
                                result = await self.perform_checkin(http_client=http_client, checkin_id=day.get('_id'))
                                if result.get('status') == "success":
                                    logger.success(self.log_message(f"Successfully checked in: {day.get('reward')} points"))
                                    break
                                else:
                                    logger.warning(self.log_message("Failed to perform checkin activity"))

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    log_error(self.log_message(f"Unknown error: {error}"))
                    await asyncio.sleep(delay=3)

                sleep_time = random.randint(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])
                logger.info(self.log_message(f"Sleep <lc>{sleep_time}s</lc>"))
                await asyncio.sleep(delay=sleep_time)


async def run_tapper(tg_client: UniversalTelegramClient):
    runner = Tapper(tg_client=tg_client)
    try:
        await runner.run()
    except InvalidSession as e:
        logger.error(runner.log_message(f"Invalid Session: {e}"))
