from typing import Optional
from discord import Embed, Forbidden, Guild, Interaction, Member, NotFound, app_commands
from discord.ext.commands import Cog, guild_only

from bot import PoxBot
from logger import logger

async def get_all_guild_members(guild: Guild):
    cached_members = guild.members

    if cached_members and guild.member_count:
        if len(cached_members) >= guild.member_count - 10:
            return cached_members
    
        try:
            full_member_list = [member async for member in guild.fetch_members(limit=None)]
            return full_member_list
        except Forbidden:
            return cached_members
        except Exception as e:
            logger.exception(e)
            return cached_members

async def get_reliable_member(guild: Guild, user_id: int) -> Optional[Member]:
    """
    Tries to get a member from the cache, falling back to an API fetch if necessary.
    Returns the discord.Member object or None if the member is not found.
    """
    
    # 1. Try the Cache (Quick)
    member = guild.get_member(user_id)
    if member is not None:
        logger.info("Member found in cache! :D")
        return member

    # 2. Fallback to API Fetch (Reliable)
    logger.warning("Member not in cache. Fetching from API...")
    try:
        # This guarantees accuracy but requires an API call (and must be awaited)
        member = await guild.fetch_member(user_id) 
        logger.info("Member successfully fetched! (:")
        return member
    except NotFound:
        # This is the expected exception if the user is NOT in the guild
        logger.error("User is NOT in the guild/server.")
        return None
    except Forbidden:
        # This happens if the bot is missing the 'Members Intent'
        logger.error("Error: Bot is missing the 'Members Intent' or required permissions! :c")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred during fetch: {e}")
        return None

class Leaderboard(Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
    
    group = app_commands.Group(name="leaderboard",description="Leaderboards")
    
    @group.command(name="pox",description="Shows leaderboard in server who said pox for many times")
    async def poxword_leaderboard(self, interaction: Interaction):
        await interaction.response.defer()
        if self.bot.db_connection:
            async with self.bot.db_connection.execute("SELECT user_id, pox_count FROM leaderboard ORDER BY pox_count DESC LIMIT 32") as cursor:
                lbdata = await cursor.fetchall()
            
            desc = ""
            
            if len(lbdata) == 0:
                desc = "No one has said \"pox\" yet."
            else:
                for i, (id,count) in enumerate(lbdata,1):
                    desc += f"{i}. <@{id}>: {int(count)} times!\n"
            
            e = Embed(
                title="**Pox Leaderboard**",
                description=desc,
                color=0xFFA500,
            )
            e.set_footer(text="The leaderboard database were stored in host computer.")
            
            await interaction.followup.send(embed=e)
        else:
            await interaction.followup.send("sorry, bot has no connection with Database.")
    
    @group.command(name="mine", description="Shows your word points for no reason")
    async def my_point(self , interaction: Interaction):
        await interaction.response.defer()

        if self.bot.db_connection:
            async with self.bot.db_connection.execute("SELECT amount FROM words WHERE user_id = ?", (interaction.user.id,)) as cursor:
                lbdata = await cursor.fetchone()
            
            desc = ""

            if lbdata:
                desc = f"You have {lbdata[0]} points."
            else:
                desc = "Nothing you got."
            
            e = Embed(title="Times you said",description=desc)
            
            await interaction.followup.send(embed=e)
        else:
            await interaction.followup.send("sorry, bot has no connection with Database.")
    
    @group.command(name="words",description="Shows leaderboard who has yapping all times")
    async def word_leaderboard(self, interaction: Interaction):
        await interaction.response.defer()
        if self.bot.db_connection:
            async with self.bot.db_connection.execute("SELECT user_id, amount FROM words ORDER BY amount DESC LIMIT 32") as cursor:
                lbdata = await cursor.fetchall()
            
            desc = ""
            
            if len(lbdata) == 0:
                desc = "No one has said \"any words\" yet."
            else:
                for i, (id,count) in enumerate(lbdata,1):
                    desc += f"{i}. <@{id}>: {int(count)} times!\n"
            
            e = Embed(
                title="**Word Leaderboard**",
                description=desc,
                color=0xFFA500,
            )
            e.set_footer(text="The leaderboard database were stored in host computer.")
            
            await interaction.followup.send(embed=e)
        else:
            await interaction.followup.send("sorry, bot has no connection with Database.")
    
    
    @group.command(name="local_words",description="Shows leaderboard in server who has yapping all times")
    @guild_only()
    async def word_leaderboard_local(self, interaction: Interaction):
        await interaction.response.defer()
        if interaction.guild is None:
            await interaction.followup.send(f"It seems you're not in the server.")
            return
        
        if self.bot.db_connection:
            async with self.bot.db_connection.execute("SELECT user_id, amount FROM words ORDER BY amount DESC LIMIT 32") as cursor:
                lbdata = await cursor.fetchall()
            
            desc = ""
            
            if len(lbdata) == 0:
                desc = "No one has said \"any words\" yet."
            else:                
                lines = []

                for i, (user_id, count) in enumerate(lbdata, 1):
                    """
                    member_obj = None

                    try:
                        member_obj = await guild.fetch_member(user_id)
                    except NotFound:
                        continue
                    except Exception as e:
                        logger.error(f"Error fetching member {user_id}: {e}")
                        continue
                    """

                    member_found = await get_reliable_member(interaction.guild, user_id)

                    if member_found:
                        lines.append(f"{i}. <@{user_id}>: **{int(count)}** times!")
                
                desc = "\n".join(lines)

                if not desc:
                    desc = "There is no member that is listed on your server."
            
            e = Embed(
                title="**Word Leaderboard**",
                description=desc,
                color=0xFFA500,
            )
            e.set_footer(text="The leaderboard database were stored in host computer.")
            
            await interaction.followup.send(embed=e)
        else:
            await interaction.followup.send("sorry, bot has no connection with Database.")

    # get specified user's word count
    @group.command(name="user_words",description="Shows specified user's word points")
    async def user_word_count(self, interaction: Interaction, user: Member):
        await interaction.response.defer()

        embed = Embed(
            title="User Word Points",
            color=0x00FF00,
        )

        if not self.bot.db_connection: return await interaction.followup.send("sorry, bot has no connection with Database.")

        async with self.bot.db_connection.execute("SELECT amount FROM words WHERE user_id = ?", (user.id,)) as cursor:
            lbdata = await cursor.fetchone()
        
        if not lbdata:
            embed.description = f"<@{user.id}> has no points."
            return await interaction.followup.send(embed=embed)
        
        embed.description = f"<@{user.id}> has {lbdata[0]} points."

        return await interaction.followup.send(embed=embed)        
            
async def setup(bot):
    await bot.add_cog(Leaderboard(bot))