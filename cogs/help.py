from typing import Optional
from discord.ext import commands
from discord import Embed, Interaction, app_commands


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help_v2")
    async def help_command(self, interaction: Interaction, index_number: Optional[int] = 0):
        if index_number is None:
            index_number = 0

        e = Embed(title="Bot Commands")
        
        all_commands = self.bot.tree.get_commands()
        
        if index_number > (round(len(all_commands)/20) - 1):
            await interaction.response.send_message("Requested search index is larger than list length.",ephemeral=True)
            return
        
        remaining = len(all_commands) - len(all_commands[:(index_number+1)*20])
        limited_commands = all_commands[(index_number*20):(index_number + 1) * 20]
        
        for command in limited_commands:
            e.add_field(name=f"/{command.name}", value=command.description or "...",inline=True)
        
        e.add_field(name="Index",value=f"{index_number}/{(round(len(all_commands)/20)-1)}")
        e.add_field(name="Remaining commands to see", value=f"{remaining} Commands")
        
        await interaction.response.send_message(embed=e, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))