[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/+jJhUfsfFCn4zZDk0)      [![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/realgoats_bot/run?startapp=333c4cc1-2ce4-4b17-99f8-7c3797832413)

## Recommendation before use

# 🔥🔥 PYTHON version must be 3.10 🔥🔥

> 🇷 🇺 README in russian available [here](README-RU.md)

## Features  
|            Feature            | Supported |
|:-----------------------------:|:---------:|
|        Multithreading         |     ✅     |
|   Proxy binding to session    |     ✅     |
|         Auto Referral         |     ✅     |
|        Auto Claim Task        |     ✅     |
| Support for telethon .session |     ✅     |


## [Settings](https://github.com/GravelFire/MajorBot/blob/main/.env-example/)
|          Settings           |                                                                                                                  Description                                                                                                                  |
|:---------------------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|    **API_ID / API_HASH**    |                                                                                   Platform data from which to run the Telegram session (default - android)                                                                                    |
|   **GLOBAL_CONFIG_PATH**    | Specifies the global path for accounts_config, proxies, sessions. <br/>Specify an absolute path or use an environment variable (default environment variable: **TG_FARM**) <br/>If no environment variable exists, uses the script directory. |
|         **REF_ID**          |                                                                                              Your referral id after startapp= (Your telegram ID)                                                                                              |
| **USE_RANDOM_DELAY_IN_RUN** |                                                                                           Whether to use random delay at startup (**True** / False)                                                                                           |
|   **RANDOM_DELAY_IN_RUN**   |                                                                                                    Random delay at startup (e.g. [0, 15])                                                                                                     |
|       **SLEEP_TIME**        |                                                                                                 Delay before the next lap (e.g. [1800, 3600])                                                                                                 |
|   **SESSIONS_PER_PROXY**    |                                                                                            Amount of sessions, that can share same proxy ( **1** )                                                                                            |
|   **USE_PROXY_FROM_FILE**   |                                                                               Whether to use a proxy from the `bot/config/proxies.txt` file (True / **False**)                                                                                |
|      **DEVICE_PARAMS**      |                                                                          Enter device settings to make the telegram session look more realistic  (True / **False**)                                                                           |
|      **DEBUG_LOGGING**      |                                                                                     Whether to log error's tracebacks to /logs folder (True / **False**)                                                                                      |

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
You can download the [**repository**](https://github.com/GravelFire/realgoats_bot) by cloning it to your system and installing the necessary dependencies:
```shell
git clone https://github.com/GravelFire/realgoats_bot.git
cd realgoats_bot
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
~/realgoats_bot >>> python3 main.py --action (1/2)
# Or
~/realgoats_bot >>> python3 main.py -a (1/2)

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
~/realgoats_bot >>> python main.py --action (1/2)
# Or
~/realgoats_bot >>> python main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```
