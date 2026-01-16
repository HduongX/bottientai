import discord
from discord.ext import commands
from database import get_money, set_money, money_lock

class Transfer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="chuyentien")
    async def chuyentien(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Số tiền không hợp lệ")

        async with money_lock:
            sender = await get_money(ctx.author.id)
            if sender < amount:
                return await ctx.send("❌ Bạn không đủ tiền")

            receiver = await get_money(member.id)

            await set_money(ctx.author.id, sender - amount)
            await set_money(member.id, receiver + amount)

        await ctx.send(
            f"💸 Đã chuyển **{amount:,} xu** cho {member.mention}"
        )

async def setup(bot):
    await bot.add_cog(Transfer(bot))
