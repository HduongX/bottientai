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
    async def add_money(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Số tiền phải lớn hơn 0")

        async with money_lock:
            current = get_money(member.id)
            set_money(member.id, current + amount)

        await ctx.send(f"✅ Đã cộng **{amount:,} xu** cho {member.mention}")

    @commands.command(name="removemoney")
    @is_admin()
    async def remove_money(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Số tiền phải lớn hơn 0")

        async with money_lock:
            current = get_money(member.id)
            if current < amount:
                return await ctx.send("❌ Người chơi không đủ tiền")

            set_money(member.id, current - amount)

        await ctx.send(f"✅ Đã trừ **{amount:,} xu** của {member.mention}")

async def setup(bot):
    await bot.add_cog(Admin(bot))
