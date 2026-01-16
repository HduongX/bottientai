from discord.ext import commands
from database import *

class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    def convert(self, xu):
        bac = xu // 100
        ngan = bac // 10
        kim = ngan // 10
        return bac, ngan, kim

    @commands.command(name="sodu")
    async def sodu(self, ctx):
        w, b, _ = get_user(ctx.author.id)
        bac, ngan, kim = self.convert(w)
        await ctx.send(
            f"💰 Ví: {w} xu\n"
            f"🏦 Bank: {b} xu\n"
            f"→ {bac} bạc | {ngan} ngân | {kim} kim"
        )

async def setup(bot):
    await bot.add_cog(Economy(bot))
