from tortoise import Tortoise
from settings import settings

# Ensure correct DB URL format
DATABASE_URL = settings.PGSQL_DATABASE_URL.replace("postgresql://", "postgres://")

# Tortoise ORM Configuration
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": "<database>",
                "host": "<host>",
                "port": 5432,
                "user": "<user>",
                "password": "<password>",
                "ssl": True,
            },
        }
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],  # ✅ Add "aerich.models"
            "default_connection": "default",
        },
    },
}

async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()
