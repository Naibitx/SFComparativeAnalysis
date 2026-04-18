from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):#this wll load environment variables from our .env

    #app settings below
    app_name: str = "AI Comparator"
    debug: bool= True

    #database setting bellow
    database_url:str = ""

    #api keys settings bellow

    #paths bellow
    workspace_dir: str= "./workspace"

    class Config:
        env_file=".env" #loads our env file

#to load just once
@lru_cache
def get_settings():
    return Settings
