from discord.ext import commands
from database import get_money

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sodu")
    async def sodu(self, ctx):
        bal = await get_money(ctx.author.id)
        await ctx.send(f"💰 Số dư của bạn: **{bal:,} xu**")

async def setup(bot):
    await bot.add_cog(Economy(bot))
