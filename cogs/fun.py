from discord.ext.commands import Cog
from discord import Member, app_commands, Interaction
import random

from matplotlib import pyplot as plt

from bot import PoxBot

from logger import logger
import asyncio

class Fun(Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
    
    @app_commands.command(name="guess_game", description="Starts a new number guessing game (1 ~ 100)")
    async def guess_game(self, interaction: Interaction):
        user_id = interaction.user.id

        if user_id in self.bot.active_games:
            await interaction.response.send_message("You already have an active game going.")
            return
        
        secret_number = random.randint(1,100)
        self.bot.active_games[user_id] = {
            'number': secret_number,
            'attempts': 0,
            'recent': 0,
        }

        await interaction.response.send_message(
            f"Guessing game started."
            f"Use /guess <number> to guess."
        )
    
    @app_commands.command(name='guess', description="Guess the number.")
    async def make_guess(self, interaction: Interaction, number: int):
        user_id = interaction.user.id

        if user_id not in self.bot.active_games:
            await interaction.response.send_message("You haven't started a game yet.")
            return
        
        game_data = self.bot.active_games[user_id]
        if not ('number','attempts') in game_data:
            await interaction.response.send_message("It seems you've choose wrong one.")
            return
        
        secret_number = game_data['number']
        game_data['attempts'] += 1
        attempts = game_data['attempts']

        if number < 1 or number > 100:
            await interaction.response.send_message("Not that so far.")
            return
        
        game_data['recent'] = number

        recent_guess = game_data['recent']

        if attempts < 16:
            if number < secret_number:
                await interaction.response.send_message("Too low.")
            elif number > secret_number:
                await interaction.response.send_message("Too high.")
            else:
                del self.bot.active_games[user_id]
                await interaction.response.send_message(
                    f"Congrats {interaction.user.name}. You've guessed my number {secret_number} in just {attempts} attempts.\nYou can play the guessing game by typing `/guess_game`."
                )
        else:
            special = ""
            distance_from_number = abs(secret_number - number)
            if distance_from_number < 2:
                special = "You were very very close to the number..."
            elif distance_from_number < 2 and distance_from_number > 8:
                special = "You were so close to the number..."
            elif distance_from_number < 8 and distance_from_number > 16:
                special = "You were a bit close to the number..."
            elif distance_from_number > 16:
                special = "You were not even close to the number."
            
            await interaction.response.send_message(f"You failed to guess. {special}\n It was {secret_number}. Try again.")
    
    @app_commands.command(name="stopguess", description="Stops the current guessing game.")
    async def stop_guessing(self, interaction: Interaction):
        user_id = interaction.user.id

        if user_id in self.bot.active_games:
            secret = self.bot.active_games[user_id]['number']
            del self.bot.active_games[user_id]
            await interaction.response.send_message(f"Aw... It was {secret}.")
        else:
            await interaction.response.send_message(f"You've not even started the guess.")

    @app_commands.command(name="job_application",description="yeah")
    async def a_job_message(self, ctx):
        try:
            await ctx.response.send_message("Today, I'll be talking about one of humanity's biggest fears.")
            await asyncio.sleep(2)
            await ctx.followup.send("# A J*B.")
        except Exception as e:
            logger.error(e)
    
    @app_commands.command(name="boop_member",description="boops someone")
    @app_commands.describe(user="Member to boop")
    async def boop_member(self, ctx: Interaction, user: Member):
        await ctx.response.send_message(f"<@{user.id}> boop.")
    
async def setup(bot):
    await bot.add_cog(Fun(bot))