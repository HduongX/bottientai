from discord.ext import commands
from database import *

def admin_only():
    async def p(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(p)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addtien")
    @admin_only()
    async def add_money(self, ctx, member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Số tiền không hợp lệ")

        async with lock:
            w, b, inv = get_user(member.id)
            update_user(member.id, wallet=w + amount)

        await ctx.send(f"✅ Đã cộng **{amount} xu** cho {member.mention}")

    @commands.command(name="trutien")
    @admin_only()
    async def remove_money(self, ctx, member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Số tiền không hợp lệ")

        async with lock:
            w, b, inv = get_user(member.id)
            if w < amount:
                return await ctx.send("❌ Không đủ tiền để trừ")

            update_user(member.id, wallet=w - amount)

        await ctx.send(f"✅ Đã trừ **{amount} xu** của {member.mention}")

async def setup(bot):
    await bot.add_cog(Admin(bot))
