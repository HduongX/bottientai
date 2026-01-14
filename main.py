import discord
from discord import app_commands
import aiosqlite
import asyncio
import os

TOKEN = os.getenv("TOKEN") or "YOUR_BOT_TOKEN"
DB_NAME = "economy.db"

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ================= LOCK SYSTEM =================
user_locks = {}

def get_user_lock(user_id: int) -> asyncio.Lock:
    if user_id not in user_locks:
        user_locks[user_id] = asyncio.Lock()
    return user_locks[user_id]

# ================= DATABASE =================
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER NOT NULL DEFAULT 1000
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS shop_items (
            item TEXT PRIMARY KEY,
            price INTEGER NOT NULL
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            user_id INTEGER,
            item TEXT,
            amount INTEGER,
            PRIMARY KEY (user_id, item)
        )
        """)
        await db.commit()

# ================= EVENTS =================
@bot.event
async def on_ready():
    await init_db()
    await tree.sync()
    print(f"✅ Bot đã online: {bot.user}")

# ================= ECONOMY =================
@tree.command(name="sodu", description="Xem số dư của bạn")
async def sodu(interaction: discord.Interaction):
    uid = interaction.user.id
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT balance FROM users WHERE user_id = ?", (uid,)
        ) as cursor:
            row = await cursor.fetchone()

        if not row:
            await db.execute(
                "INSERT INTO users (user_id, balance) VALUES (?, 1000)",
                (uid,)
            )
            await db.commit()
            balance = 1000
        else:
            balance = row[0]

    await interaction.response.send_message(
        f"💰 **Số dư của bạn:** {balance:,} xu"
    )

# ================= SHOP =================
@tree.command(name="cuahang", description="Xem cửa hàng")
async def cuahang(interaction: discord.Interaction):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT item, price FROM shop_items") as cursor:
            items = await cursor.fetchall()

    if not items:
        return await interaction.response.send_message("❌ Cửa hàng đang trống")

    msg = "🛒 **CỬA HÀNG**\n"
    for item, price in items:
        msg += f"• **{item}** — {price:,} xu\n"

    await interaction.response.send_message(msg)

# ================= BUY =================
@tree.command(name="mua", description="Mua vật phẩm")
@app_commands.describe(item="Tên vật phẩm", amount="Số lượng")
async def mua(interaction: discord.Interaction, item: str, amount: int = 1):
    if amount <= 0:
        return await interaction.response.send_message(
            "❌ Số lượng không hợp lệ", ephemeral=True
        )

    uid = interaction.user.id
    lock = get_user_lock(uid)

    async with lock:
        async with aiosqlite.connect(DB_NAME) as db:
            try:
                await db.execute("BEGIN IMMEDIATE")

                async with db.execute(
                    "SELECT price FROM shop_items WHERE item = ?",
                    (item.lower(),)
                ) as cursor:
                    row = await cursor.fetchone()

                if not row:
                    await db.execute("ROLLBACK")
                    return await interaction.response.send_message(
                        "❌ Item không tồn tại", ephemeral=True
                    )

                price = row[0]
                total = price * amount

                async with db.execute(
                    "SELECT balance FROM users WHERE user_id = ?",
                    (uid,)
                ) as cursor:
                    row = await cursor.fetchone()

                if not row or row[0] < total:
                    await db.execute("ROLLBACK")
                    return await interaction.response.send_message(
                        "❌ Bạn không đủ tiền", ephemeral=True
                    )

                await db.execute(
                    "UPDATE users SET balance = balance - ? WHERE user_id = ?",
                    (total, uid)
                )

                await db.execute("""
                INSERT INTO inventory (user_id, item, amount)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, item)
                DO UPDATE SET amount = amount + ?
                """, (uid, item.lower(), amount, amount))

                await db.commit()

            except Exception as e:
                await db.execute("ROLLBACK")
                return await interaction.response.send_message(
                    f"❌ Lỗi giao dịch", ephemeral=True
                )

    await interaction.response.send_message(
        f"✅ Bạn đã mua **{amount} {item}** với giá **{total:,} xu**"
    )

# ================= PAY =================
@tree.command(name="chuyentien", description="Chuyển tiền cho người khác")
@app_commands.describe(user="Người nhận", amount="Số tiền")
async def chuyentien(interaction: discord.Interaction, user: discord.Member, amount: int):
    sender = interaction.user.id
    receiver = user.id

    if sender == receiver:
        return await interaction.response.send_message(
            "❌ Không thể tự chuyển tiền cho chính mình", ephemeral=True
        )

    if amount <= 0:
        return await interaction.response.send_message(
            "❌ Số tiền không hợp lệ", ephemeral=True
        )

    lock = get_user_lock(sender)

    async with lock:
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute(
                "SELECT balance FROM users WHERE user_id = ?",
                (sender,)
            ) as cursor:
                row = await cursor.fetchone()

            if not row or row[0] < amount:
                return await interaction.response.send_message(
                    "❌ Bạn không đủ tiền", ephemeral=True
                )

            await db.execute(
                "UPDATE users SET balance = balance - ? WHERE user_id = ?",
                (amount, sender)
            )

            await db.execute("""
            INSERT INTO users (user_id, balance)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET balance = balance + ?
            """, (receiver, amount, amount))

            await db.commit()

    await interaction.response.send_message(
        f"💸 Bạn đã chuyển **{amount:,} xu** cho **{user.display_name}**"
    )

# ================= RUN =================
bot.run(TOKEN)
