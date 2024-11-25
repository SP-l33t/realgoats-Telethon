import aiohttp
import asyncio
import json
from urllib.parse import unquote, parse_qs
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector, SocksError
from better_proxy import Proxy
from random import uniform, randint, sample
from tenacity import retry, stop_after_attempt, wait_incrementing, retry_if_exception_type
from time import time

from bot.utils.universal_telegram_client import UniversalTelegramClient

from bot.config import settings
from bot.utils import logger, log_error, config_utils, date_utils, CONFIG_PATH, first_run
from bot.exceptions import InvalidSession
from .headers import headers, get_sec_ch_ua

API_CATCHING = "https://api-catching.goatsbot.xyz"
API_CHECKIN = "https://api-checkin.goatsbot.xyz"
API_DOGS = "https://api-dogs.goatsbot.xyz"
API_ME = "https://api-me.goatsbot.xyz"
API_MISSION = "https://api-mission.goatsbot.xyz"
DEV_API = "https://dev-api.goatsbot.xyz"
DEV_API_V2 = "https://dev-api-v2.goatsbot.xyz"


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

    @retry(stop=stop_after_attempt(4),
           wait=wait_incrementing(1, 4),
           retry=retry_if_exception_type((
                   asyncio.exceptions.TimeoutError,
                   aiohttp.ServerDisconnectedError,
                   aiohttp.ClientProxyConnectionError,
                   SocksError
           )))
    async def make_request(self, http_client: CloudflareScraper, method, url=None, **kwargs):
        response = await http_client.request(method, url, **kwargs)
        if response.status in range(200, 300):
            return await response.json() if 'json' in response.content_type else await response.text()
        else:
            error_json = await response.json() if 'json' in response.content_type else {}
            error_text = f"Error: {error_json}" if error_json else ""
            if settings.DEBUG_LOGGING:
                logger.warning(self.log_message(
                    f"{method} Request to {url} failed with {response.status} code. {error_text}"))
            return error_json

    async def login(self, http_client: CloudflareScraper, init_data):
        rawdata = {'Rawdata': init_data}
        return await self.make_request(http_client, 'POST', url=f"{DEV_API}/auth/login", json={}, headers=rawdata)

    async def get_me_info(self, http_client: CloudflareScraper):
        return await self.make_request(http_client, 'GET', url=f"{API_ME}/users/me")

    async def get_goat_pass_info(self, http_client: CloudflareScraper):
        return await self.make_request(http_client, 'GET', url=f"{DEV_API_V2}/users/goat-pass")

    async def get_tasks(self, http_client: CloudflareScraper) -> dict:
        return await self.make_request(http_client, 'GET', url=f'{API_MISSION}/missions/user')

    async def done_task(self, http_client: CloudflareScraper, task_id: str):
        return await self.make_request(http_client, 'POST', url=f'{DEV_API}/missions/action/{task_id}')

    async def get_checkin_options(self, http_client: CloudflareScraper):
        return await self.make_request(http_client, 'GET', url=f"{API_CHECKIN}/checkin/user")

    async def perform_checkin(self, http_client: CloudflareScraper, checkin_id: str):
        return await self.make_request(http_client, 'POST', url=f'{API_CHECKIN}/checkin/action/{checkin_id}')

    async def get_cinema(self, http_client: CloudflareScraper):
        return (await self.make_request(http_client, 'GET', url=f"{DEV_API}/goat-cinema")).get('remainTime', 0)

    async def watch_movie(self, http_client: CloudflareScraper):
        return await self.make_request(http_client, 'POST', url=f"{DEV_API}/goat-cinema/watch")

    async def get_catching_game_info(self, http_client: CloudflareScraper):
        return await self.make_request(http_client,'GET', url=f"{API_CATCHING}/catching")

    async def start_new_game(self, http_client: CloudflareScraper, location: int, bet_amount: int):
        payload = {"location": location, "bomb": 5, "bet_amount": bet_amount}
        await self.make_request(http_client, 'OPTIONS', url=f"{API_CATCHING}/catching/new-game")
        response = await self.make_request(http_client, 'POST', url=f"{API_CATCHING}/catching/new-game", json=payload)
        if response.get('message', "") == "Too many requests from this user":
            await asyncio.sleep(5, 10)
            return await self.start_new_game(http_client, location, bet_amount)
        else:
            return response

    async def continue_game(self, http_client: CloudflareScraper, location: int, game_id, opt: bool = False):
        if opt:
            await self.make_request(http_client, 'OPTIONS', url=f"{API_CATCHING}/catching/continue-game/{game_id}")
        payload = {"location": location}
        response = await self.make_request(http_client, 'POST', url=f"{API_CATCHING}/catching/continue-game/{game_id}",
                                           json=payload)
        if response.get('message', "") == "Too many requests from this user":
            await asyncio.sleep(3, 5)
            return await self.continue_game(http_client, location, game_id)
        else:
            return response

    async def cashout_game(self, http_client: CloudflareScraper, game_id):
        await self.make_request(http_client, 'OPTIONS', url=f"{API_CATCHING}/catching/cashout/{game_id}")
        response = await self.make_request(http_client, 'POST', url=f"{API_CATCHING}/catching/cashout/{game_id}")
        if response.get('message', "") == "Too many requests from this user":
            await asyncio.sleep(3, 5)
            return await self.cashout_game(http_client, game_id)
        else:
            return response

    async def run(self) -> None:
        random_delay = uniform(1, settings.SESSION_START_DELAY)
        logger.info(self.log_message(f"Bot will start in <lr>{int(random_delay)}s</lr>"))
        await asyncio.sleep(delay=random_delay)

        access_token_created_time = 0
        init_data = None

        token_live_time = uniform(3500, 3600)

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
                        logger.info(self.log_message(f"🐐 Login failed. Sleep <lc>300</lc>s"))
                        await asyncio.sleep(300)
                        continue

                    if self.tg_client.is_fist_run:
                        await first_run.append_recurring_session(self.session_name)
                    http_client.headers['Authorization'] = f'Bearer {access_token}'
                    balance = (await self.get_me_info(http_client=http_client)).get('balance')
                    pass_info = await self.get_goat_pass_info(http_client)
                    pass_pts = pass_info.get('userStat', {}).get('pass_point', 0)
                    gambling_progress = round(pass_info.get('userStat', {}).get('totalEarn', 0) / 10000000 * 100, 2)
                    logger.info(self.log_message(
                        f"🐐 <lc>Login successful</lc> | Balance: <lc>{balance}</lc> | Pass points: <lc>{pass_pts}</lc>"
                        f" | Gambling progress: <lc>{gambling_progress}%</lc>"))

                    tasks = await self.get_tasks(http_client=http_client)
                    for project, project_tasks in tasks.items():
                        for task in project_tasks:
                            if not task.get('status') or task.get('cooldown_time'):
                                task_id = task.get('_id')
                                task_name = task.get('name')
                                task_reward = task.get('reward')

                                logger.info(self.log_message(f"Attempting task: {project}: {task_name}"))

                                done_result = await self.done_task(http_client=http_client, task_id=task_id)

                                if done_result and done_result.get('status') == 'success':
                                    logger.info(self.log_message(
                                        f"Task completed successfully: <lc>{project}</lc>: <lc>{task_name}</lc> | "
                                        f"Reward: <lc>{task_reward} coins</lc>"))
                                else:
                                    logger.warning(self.log_message(
                                        f"Failed to complete task: <lc>{project}</lc>: <lc>{task_name}</lc>"))

                                await asyncio.sleep(uniform(3, 7))

                    checkin = await self.get_checkin_options(http_client=http_client)
                    last_checkin = checkin.get('lastCheckinTime')
                    if checkin and last_checkin is not None:
                        for day in checkin.get('result', []):
                            if (last_checkin == 0 or date_utils.is_next_day(last_checkin)) and day.get('status') is False:
                                result = await self.perform_checkin(http_client=http_client, checkin_id=day.get('_id'))
                                if result.get('status') == "success":
                                    logger.success(self.log_message(
                                        f"Successfully checked in: {day.get('reward')} points"))
                                    break
                                else:
                                    logger.warning(self.log_message("Failed to perform checkin activity"))

                    await asyncio.sleep(uniform(2, 5))
                    for _ in range(await self.get_cinema(http_client)):
                        reward = await self.watch_movie(http_client)
                        amount = reward.get('reward')
                        if amount:
                            logger.success(self.log_message(
                                f"Watched a movie. Reward: <lc>{amount} {reward.get('unit')}</lc>"))
                            await asyncio.sleep(uniform(5, 15))
                        else:
                            logger.warning(self.log_message("Failed to watch a movie"))
                            break

                    if settings.ENABLE_GAMBLING and not gambling_progress >= 100:
                        games_left = randint(settings.MAX_GAMES//2, settings.MAX_GAMES)
                        balance = (await self.get_me_info(http_client=http_client)).get('balance', 0)
                        game = await self.get_catching_game_info(http_client)
                        bet_amount = max(int(balance * 0.00025), 100)
                        if balance > settings.MIN_GAMBLING_BALANCE:
                            while True:
                                games_left -= 1
                                if bet_amount > balance or bet_amount < 100:
                                    logger.info(self.log_message(f"Not enough money to gamble. Balance: {balance}"))
                                    break
                                elif balance <= settings.MIN_GAMBLING_BALANCE:
                                    logger.info(self.log_message(f"Balance is less than MIN_GAMBLING_BALANCE. "
                                                                 f"Stopping gambling. Balance: {balance}"))
                                    break
                                await asyncio.sleep(uniform(7, 10))
                                moves = []
                                if not game.get('stateGame') or game.get('stateGame', {}).get('is_completed'):
                                    moves = sample(range(1, 17), 2)
                                    game = await self.start_new_game(http_client, moves[0], bet_amount)
                                    game_id = game.get('stateGame', {}).get('_id')
                                    balance = game.get("user", {}).get('balance', 0)
                                    if game.get('stateGame', {}).get('bomb_location', []):
                                        logger.info(self.log_message(f"Game lost. <lc>-{bet_amount}</lc> coins | "
                                                                     f"Balance: <lc>{balance}</lc>"))
                                        bet_amount = int(bet_amount * 2)
                                        game = {}
                                        continue
                                elif game.get('stateGame', {}).get('_id'):
                                    game_id = game.get('stateGame', {}).get('_id')

                                if game_id:
                                    can_claim = True
                                    send_opt = True
                                    for x in moves[1:] if moves else range(0):
                                        await asyncio.sleep(uniform(1, 5))
                                        continue_game = await self.continue_game(http_client, x, game_id, send_opt)
                                        if continue_game.get('message', "") == 'Game cashout completed':
                                            can_claim = False
                                            break
                                        balance = continue_game.get('user', {}).get('balance', 0)
                                        send_opt = False
                                        if continue_game.get('stateGame', {}).get('bomb_location', []):
                                            logger.info(self.log_message(f"Game lost. <lc>-{bet_amount}</lc> coins | "
                                                                         f"Balance: <lc>{balance}</lc>"))
                                            can_claim = False
                                            bet_amount = int(bet_amount * 2)
                                            break

                                    if can_claim:
                                        await asyncio.sleep(uniform(1, 5))
                                        result = await self.cashout_game(http_client, game_id)
                                        if result.get('message', "") == 'Game cashout completed':
                                            game = {}
                                            continue
                                        balance = result.get('user', {}).get('balance', 0)
                                        reward = result.get('stateGame', {}).get('reward', 0)
                                        bet_amount = result.get('stateGame', {}).get('bet_amount', 0)
                                        if balance:
                                            logger.success(self.log_message(
                                                f"Game won. Got <lc>{reward-bet_amount}</lc> coins | "
                                                f"Balance: <lc>{balance}</lc>"))
                                            if games_left <= 0:
                                                break
                                        bet_amount = max(int(balance * 0.00025), 100)

                                    game = {}

                    sleep_time = uniform(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])
                    logger.info(self.log_message(f"Sleep <lc>{int(sleep_time)}s</lc>"))
                    await asyncio.sleep(sleep_time)

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    sleep_time = uniform(60, 120)
                    log_error(self.log_message(f"Unknown error: {error}. Sleep <lc>{int(sleep_time)}</lc> seconds"))
                    await asyncio.sleep(sleep_time)


async def run_tapper(tg_client: UniversalTelegramClient):
    runner = Tapper(tg_client=tg_client)
    try:
        await runner.run()
    except InvalidSession as e:
        logger.error(runner.log_message(f"Invalid Session: {e}"))
