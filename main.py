import os
import asyncio
import discord
from discord.ext import commands
from database import init_db

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

EXTENSIONS = [
    "economy",
    "shop",
    "transfer",
    "admin"
]

async def main():
    await init_db()

    async with bot:
        for ext in EXTENSIONS:
            try:
                await bot.load_extension(ext)
                print(f"Loaded {ext}")
            except Exception as e:
                print(f"❌ Failed {ext}: {e}")

        await bot.start(os.getenv("BOT_TOKEN"))

asyncio.run(main())
