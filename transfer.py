from discord.ext import commands
from database import *

class Transfer(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command(name="chuyentien")
    async def transfer(self, ctx, member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Số tiền không hợp lệ")

        async with lock:
            w, b, inv = get_user(ctx.author.id)
            if w < amount:
                return await ctx.send("❌ Không đủ xu")

            rw, rb, rinv = get_user(member.id)

            update_user(ctx.author.id, wallet=w - amount)
            update_user(member.id, wallet=rw + amount)

        await ctx.send(f"✅ Đã chuyển **{amount} xu** cho {member.mention}")

async def setup(bot):
    await bot.add_cog(Transfer(bot))
