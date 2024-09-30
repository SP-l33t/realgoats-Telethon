[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/+jJhUfsfFCn4zZDk0)      [![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/realgoats_bot/run?startapp=333c4cc1-2ce4-4b17-99f8-7c3797832413)

## Рекомендация перед использованием

# 🔥🔥 Используйте PYTHON версии 3.10 🔥🔥

> 🇪🇳 README in english available [here](README)

## Функционал  
|                               Функционал                               | Поддерживается |
|:----------------------------------------------------------------------:|:--------------:|
|                            Многопоточность                             |       ✅        | 
|                        Привязка прокси к сессии                        |       ✅        | 
|                   Авто Реферальство ваших аккаунтов                    |       ✅        |
| Авто выполнение заданий, которые можно выполнить обычному пользователю |       ✅        |
|                      Поддержка telethon .session                       |       ✅        |


## [Настройки](https://github.com/GravelFire/b_usersbot/blob/main/.env-example/)
|          Настройки          |                                                                                                                              Описание                                                                                                                               |
|:---------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|    **API_ID / API_HASH**    |                                                                                         Данные платформы, с которой будет запущена сессия Telegram (по умолчанию - android)                                                                                         |
|   **GLOBAL_CONFIG_PATH**    | Определяет глобальный путь для accounts_config, proxies, sessions. <br/>Укажите абсолютный путь или используйте переменную окружения (по умолчанию - переменная окружения: **TG_FARM**)<br/> Если переменной окружения не существует, использует директорию скрипта |
|         **REF_ID**          |                                                                                               Ваш идентификатор реферала после startapp= (Ваш идентификатор telegram)                                                                                               |
| **USE_RANDOM_DELAY_IN_RUN** |                                                                                                  Использовать ли рандомную задержку при запуске (**True** / False)                                                                                                  |
|   **RANDOM_DELAY_IN_RUN**   |                                                                                                           Рандомная задержка при запуске (напр. [0, 15])                                                                                                            |
|       **SLEEP_TIME**        |                                                                                                      Задержка перед следующим кругом (например, [1800, 3600])                                                                                                       |
|   **SESSIONS_PER_PROXY**    |                                                                                           Количество сессий, которые могут использовать один прокси (По умолчанию **1** )                                                                                           |
|   **USE_PROXY_FROM_FILE**   |                                                                                             Использовать ли прокси из файла `bot/config/proxies.txt` (**True** / False)                                                                                             |
|  **DISABLE_PROXY_REPLACE**  |                                                                                   Отключить автоматическую проверку и замену нерабочих прокси перед стартом ( True / **False** )                                                                                    |
|      **DEVICE_PARAMS**      |                                                                                  Вводить параметры устройства, чтобы сделать сессию более похожую, на реальную  (True / **False**)                                                                                  |
|      **DEBUG_LOGGING**      |                                                                                               Включить логирование трейсбэков ошибок в папку /logs (True / **False**)                                                                                               |

## Быстрый старт 📚

Для быстрой установки и последующего запуска - запустите файл run.bat на Windows или run.sh на Линукс

## Предварительные условия
Прежде чем начать, убедитесь, что у вас установлено следующее:
- [Python](https://www.python.org/downloads/) **версии 3.10**

## Получение API ключей
1. Перейдите на сайт [my.telegram.org](https://my.telegram.org) и войдите в систему, используя свой номер телефона.
2. Выберите **"API development tools"** и заполните форму для регистрации нового приложения.
3. Запишите `API_ID` и `API_HASH` в файле `.env`, предоставленные после регистрации вашего приложения.

## Установка
Вы можете скачать [**Репозиторий**](https://github.com/GravelFire/realgoats_bot) клонированием на вашу систему и установкой необходимых зависимостей:
```shell
git clone https://github.com/GravelFire/realgoats_bot.git
cd realgoats_bot
```

Затем для автоматической установки введите:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux ручная установка
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH , остальное берется по умолчанию
python3 main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/realgoats_bot >>> python3 main.py --action (1/2)
# Or
~/realgoats_bot >>> python3 main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```


# Windows ручная установка
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Указываете ваши API_ID и API_HASH, остальное берется по умолчанию
python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/realgoats_bot >>> python main.py --action (1/2)
# Или
~/realgoats_bot >>> python main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```
