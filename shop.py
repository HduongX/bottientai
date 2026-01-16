from discord.ext import commands

SHOP_ITEMS = {
    "kiem": 500,
    "giap": 800,
    "cung": 300
}

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shop")
    async def shop(self, ctx):
        msg = "🛒 **CỬA HÀNG**\n"
        for item, price in SHOP_ITEMS.items():
            msg += f"- `{item}` : {price:,} xu\n"
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(Shop(bot))
