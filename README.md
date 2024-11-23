[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/+jJhUfsfFCn4zZDk0)      [![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/realgoats_bot/run?startapp=d3f52790-77b5-4809-a0ea-56b4e4ba1ee6)

## Recommendation before use

# 🔥🔥 PYTHON version must be 3.10 🔥🔥

> 🇷 🇺 README in russian available [here](README-RU.md)

## Features  
|                 Feature                 | Supported |
|:---------------------------------------:|:---------:|
|             Multithreading              |     ✅     |
|        Proxy binding to session         |     ✅     |
|              Auto Referral              |     ✅     |
|             Auto Claim Task             |     ✅     |
| Supports telethon AND pyrogram .session |     ✅     |

_Script searches for session files in the following folders:_
* /sessions
* /sessions/pyrogram
* /session/telethon


## [Settings](https://github.com/SP-l33t/MajorBot/blob/main/.env-example/)
|         Settings          |                                                                                                                  Description                                                                                                                  |
|:-------------------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|   **API_ID / API_HASH**   |                                                                                   Platform data from which to run the Telegram session (default - android)                                                                                    |
|  **GLOBAL_CONFIG_PATH**   | Specifies the global path for accounts_config, proxies, sessions. <br/>Specify an absolute path or use an environment variable (default environment variable: **TG_FARM**) <br/>If no environment variable exists, uses the script directory. |
|      **SESSIONS_WL**      |                                                                       Specify only the names of the sessions to be run. Be sure to use double quotes (["asd", "15123])                                                                        |
|      **SESSIONS_BL**      |                                                                    Specify the names of sessions that will NOT be started. Be sure to use double quotes (["asd", "15123])                                                                     | |
|       **FIX_CERT**        |                                                                                           Try to fix  SSLCertVerificationError ( True / **False** )                                                                                           |
|        **REF_ID**         |                                                                                              Your referral id after startapp= (Your telegram ID)                                                                                              |
|  **SESSION_START_DELAY**  |                                                                                       Random delay at session start from 1 to set value (e.g. **360**)                                                                                        |
|      **SLEEP_TIME**       |                                                                                                 Delay before the next lap (e.g. [1800, 3600])                                                                                                 |
|    **ENABLE_GAMBLING**    |                                                                                                     Enable gambling ( True / **False** )                                                                                                      |
| **MIN_GAMBLING_BALANCE**  |                                                                                             Minimal balance required for gambling ( **100000** )                                                                                              |
|       **MAX_GAMES**       |                                                                                              Max amount of gambling games per cycyle ( **100** )                                                                                              |
|  **SESSIONS_PER_PROXY**   |                                                                                            Amount of sessions, that can share same proxy ( **1** )                                                                                            |
|  **USE_PROXY_FROM_FILE**  |                                                                               Whether to use a proxy from the `bot/config/proxies.txt` file (**True** / False)                                                                                |
| **DISABLE_PROXY_REPLACE** |                                                                      Disable automatic checking and replacement of non-working proxies before startup (True / **False**)                                                                      |
|     **DEVICE_PARAMS**     |                                                                          Enter device settings to make the telegram session look more realistic  (True / **False**)                                                                           |
|     **DEBUG_LOGGING**     |                                                                                     Whether to log error's tracebacks to /logs folder (True / **False**)                                                                                      |

## Quick Start 📚

To fast install libraries and run bot - open run.bat on Windows or run.sh on Linux

## Prerequisites
Before you begin, make sure you have the following installed:
- [Python](https://www.python.org/downloads/) **version 3.10**

## Obtaining API Keys
1. Go to my.telegram.org and log in using your phone number.
2. Select "API development tools" and fill out the form to register a new application.
3. Record the API_ID and API_HASH provided after registering your application in the .env file.

## Installation
You can download the [**repository**](https://github.com/SP-l33t/realgoats-Telethon) by cloning it to your system and installing the necessary dependencies:
```shell
git clone https://github.com/SP-l33t/realgoats-Telethon.git
cd realgoats-Telethon
```

Then you can do automatic installation by typing:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux manual installation
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must specify your API_ID and API_HASH, the rest is taken by default
python3 main.py
```

You can also use arguments for quick start, for example:
```shell
~/realgoats-Telethon >>> python3 main.py --action (1/2)
# Or
~/realgoats-Telethon >>> python3 main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```

# Windows manual installation
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Here you must specify your API_ID and API_HASH, the rest is taken by default
python main.py
```

You can also use arguments for quick start, for example:
```shell
~/realgoats-Telethon >>> python main.py --action (1/2)
# Or
~/realgoats-Telethon >>> python main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```
