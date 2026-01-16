from discord.ext import commands
from database import *

def admin():
    async def p(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(p)

class Shop(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command(name="shop")
    async def shop(self, ctx):
        cursor.execute("SELECT * FROM shop")
        rows = cursor.fetchall()
        if not rows:
            return await ctx.send("🛒 Shop trống")

        msg = "**🛒 SHOP**\n"
        for i, p in rows:
            msg += f"- `{i}` : {p} xu\n"
        await ctx.send(msg)

    @commands.command(name="mua")
    async def buy(self, ctx, item: str, sl: int = 1):
        cursor.execute("SELECT price FROM shop WHERE item=?", (item,))
        r = cursor.fetchone()
        if not r:
            return await ctx.send("❌ Item không tồn tại")

        price = r[0] * sl

        async with lock:
            w, b, inv = get_user(ctx.author.id)
            if w < price:
                return await ctx.send("❌ Không đủ xu")

            inv[item] = inv.get(item, 0) + sl
            update_user(ctx.author.id, wallet=w - price, inv=inv)

        await ctx.send(f"✅ Mua {sl} **{item}** (-{price} xu)")

    @commands.command(name="kho")
    async def inventory(self, ctx):
        _, _, inv = get_user(ctx.author.id)
        if not inv:
            return await ctx.send("🎒 Kho trống")

        msg = "**🎒 KHO ĐỒ**\n"
        for i, s in inv.items():
            msg += f"- {i} x{s}\n"
        await ctx.send(msg)

    @commands.command(name="addshop")
    @admin()
    async def addshop(self, ctx, item: str, price: int):
        cursor.execute("INSERT OR REPLACE INTO shop VALUES (?,?)", (item, price))
        db.commit()
        await ctx.send(f"✅ Đã thêm `{item}` ({price} xu) vào shop")

async def setup(bot):
    await bot.add_cog(Shop(bot))
