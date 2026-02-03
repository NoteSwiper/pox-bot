import random
from discord import Color, Embed, Interaction, app_commands
from discord.ext import commands
import aiosqlite
import time

from os.path import join

from bot import PoxBot
from logger import logger

class EconomyUser:
    def __init__(self, user_id: int, wallet: int, bank: int, last_daily: int):
        self.user_id = user_id
        self.wallet = wallet
        self.bank = bank
        self.last_daily = last_daily
    
    @property
    def total_money(self) -> int:
        return self.wallet + self.bank

class EconomyManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    async def setup(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    wallet INTEGER DEFAULT 0,
                    bank INTEGER DEFAULT 0,
                    last_daily INTEGER DEFAULT 0
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    description TEXT,
                    timestamp INTEGER NOT NULL
                )
            """)
            await db.commit()
        logger.info("Economy Database initialized and tables are ready")
    
    async def get_user(self, user_id: int) -> EconomyUser:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()

            if row:
                user = EconomyUser(user_id=row[0], wallet=row[1], bank=row[2], last_daily=row[3])
                return user
            else:
                await db.execute(
                    "INSERT INTO users (user_id, wallet, bank, last_daily) VALUES (?, ?, ?, ?)",
                    (user_id, 0, 0, 0)
                )
                await db.commit()
                return EconomyUser(user_id=user_id, wallet=0, bank=0, last_daily=0)

    async def update_user(self, user: EconomyUser):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET wallet = ?, bank = ?, last_daily = ? WHERE user_id = ?",
                (user.wallet, user.bank, user.last_daily, user.user_id)
            )
            await db.commit()
            
    async def log_transaction(self, user_id: int, tx_type: str, amount: int, description: str):
        timestamp = int(time.time())
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO transactions (user_id, type, amount, description, timestamp) VALUES (?, ?, ?, ?, ?)",
                (user_id, tx_type, amount, description, timestamp)
            )
            await db.commit()

class Economy(commands.Cog):
    group = app_commands.Group(name="economy", description="Economy Group.")
    def __init__(self, bot: PoxBot):
        self.bot = bot
        self.manager = EconomyManager(join(self.bot.root_path, "data/economy.db"))
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.manager.setup()
        logger.info("Cog is fully loaded and listening.")
    
    @group.command(name="balance", description="Get a balance.")
    async def balance(self, interaction: Interaction):
        user = await self.manager.get_user(interaction.user.id)

        embed = Embed(
            title=f"{interaction.user.name}'s Financial Report",
            color=Color.gold()
        )

        embed.add_field(name="Wallet", value=f"`{user.wallet:,}` coins", inline=True)
        embed.add_field(name="Bank", value=f"`{user.bank:,}` coins", inline=True)
        embed.add_field(name="Total", value=f"`{user.total_money:,}` coins", inline=False)

        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    
    @group.command(name='daily')
    async def daily(self, interaction: Interaction):
        user = await self.manager.get_user(interaction.user.id)
        current_time = int(time.time())
        
        cooldown_seconds = 60 * 60 * 24 # 24 hours
        time_since_last_daily = current_time - user.last_daily
        
        if time_since_last_daily < cooldown_seconds:
            remaining_time = cooldown_seconds - time_since_last_daily
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            
            await interaction.response.send_message(
                f"Woah there, speedy. You can claim your next daily in **{hours}h {minutes}m**."
            )
        else:
            reward = random.randint(300,600)
            user.wallet += reward
            user.last_daily = current_time
            
            await self.manager.update_user(user)

            await self.manager.log_transaction(
                user_id=interaction.user.id, 
                tx_type='daily', 
                amount=reward, 
                description=f"Claimed daily reward"
            )
            
            await interaction.response.send_message(
                f"🎉 Congrats, **{interaction.user.name}**! You claimed `{reward:,}` coins for your daily reward."
            )

    @group.command(name='work')
    async def work(self, interaction: Interaction):
        user = await self.manager.get_user(interaction.user.id)
        current_time = int(time.time())
        reward = int(40+((random.random() ** 5)*1000))
        user.wallet += reward
        user.last_daily = current_time
        
        await self.manager.update_user(user)
        await self.manager.log_transaction(
            user_id=interaction.user.id, 
            tx_type='work', 
            amount=reward, 
            description=f"Claimed by getting smth"
        )
        
        await interaction.response.send_message(
            f"🎉 Congrats, **{interaction.user.name}**! You claimed `{reward:,}` coins for uh yeah."
        )


    @group.command(name='history')
    async def history(self, interaction: Interaction, limit: int = 5):
        
        limit = max(1, min(10, limit)) 

        async with aiosqlite.connect(self.manager.db_path) as db:
            cursor = await db.execute(
                "SELECT type, amount, timestamp, description FROM transactions WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (interaction.user.id, limit)
            )
            rows = await cursor.fetchall()

        if not rows:
            return await interaction.response.send_message("You haven't made any transactions yet. Get started with `!daily` to see a log entry :P")

        embed = Embed(
            title=f"{interaction.user.name}'s Transaction History (Last {len(rows)})",
            color=Color.blue()
        )
        embed.set_footer(text="A positive amount means coins were added.")

        for row in rows:
            tx_type, amount, timestamp, description = row
            date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
            
            sign = "+" if amount >= 0 else "" 

            name = f"[{tx_type.upper()}] | {sign}{amount:,} coins"
            value = f"**Time:** {date_str} UTC\n**Note:** {description}"
            embed.add_field(name=name, value=value, inline=False)
            
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))