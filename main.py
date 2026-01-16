import os, discord, asyncio
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

EXTS = ["economy", "shop", "transfer"]

async def main():
    async with bot:
        for e in EXTS:
            await bot.load_extension(e)
        await bot.start(os.getenv("BOT_TOKEN"))

asyncio.run(main())
