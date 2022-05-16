import os

def get_postgres_url():
    driver = os.getenv("POSTGRES_DRIVER", "asyncpg")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    server = os.getenv("POSTGRES_SERVER", "devices_db")
    db = os.getenv("POSTGRES_DB", "postgres")
    return f"postgresql+{driver}://{user}:{password}@{server}/{db}"


def get_postgres_dsn():
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    server = os.getenv("POSTGRES_SERVER", "devices_db")
    db = os.getenv("POSTGRES_DB", "postgres")
    return f"dbname={db} user={user} password={password} host={server}"


def get_redis_url():
    server = os.getenv("REDIS_SERVER", "anagrams_db") 
    return f"redis://{server}"