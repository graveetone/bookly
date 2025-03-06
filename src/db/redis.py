import aioredis
from src.config import Config

JTI_EXPIRY = 60 * 60

token_blocklist = aioredis.StrictRedis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=0,
)


async def add_jti_to_blocklist(jti: str):
    await token_blocklist.set(
        name=jti,
        value="",
        ex=JTI_EXPIRY,
    )


async def jti_in_blocklist(jti: str) -> bool:
    return await token_blocklist.get(name=jti) is not None
