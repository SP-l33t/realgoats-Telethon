from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str
    GLOBAL_CONFIG_PATH: str = "TG_FARM"

    FIX_CERT: bool = False

    REF_ID: str = "d3f52790-77b5-4809-a0ea-56b4e4ba1ee6"
    SESSION_START_DELAY: int = 360
    SLEEP_TIME: list[int] = [3600, 10800]

    ENABLE_GAMBLING: bool = False
    MIN_GAMBLING_BALANCE: int = 100000
    MAX_GAMES: int = 100

    SESSIONS_PER_PROXY: int = 1
    USE_PROXY_FROM_FILE: bool = True
    DISABLE_PROXY_REPLACE: bool = False
    USE_PROXY_CHAIN: bool = False

    DEVICE_PARAMS: bool = False

    DEBUG_LOGGING: bool = False


settings = Settings()
