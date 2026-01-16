import discord
from discord.ext import commands
from database import get_money, set_money, money_lock

def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addmoney")
    @is_admin()
    async def addmoney(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Số tiền không hợp lệ")

        async with money_lock:
            bal = await get_money(member.id)
            await set_money(member.id, bal + amount)

        await ctx.send(
            f"✅ Đã cộng **{amount:,} xu** cho {member.mention}"
        )

    @commands.command(name="setmoney")
    @is_admin()
    async def setmoney(self, ctx, member: discord.Member, amount: int):
        async with money_lock:
            await set_money(member.id, amount)

        await ctx.send(
            f"⚙️ Đã set tiền của {member.mention} = **{amount:,} xu**"
        )

async def setup(bot):
    await bot.add_cog(Admin(bot))
