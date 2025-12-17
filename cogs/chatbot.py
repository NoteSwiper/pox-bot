import time
import discord
from discord.ext import commands, tasks
from discord import Activity, ActivityType, CustomActivity, Embed, Interaction, InteractionType, Message, Status, app_commands

import lmstudio as lms

from bot import PoxBot
from logger import logger

class ChatbotCog(commands.Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot

    group = app_commands.Group(name="ai", description="Chat with Gemma 3 1b yea")

    @group.command(name="chat", description="Chat with Gemma3-1b")
    async def chat_ai(self, interaction: Interaction, prompt: str):
        await interaction.response.defer()
        api_host = await lms.AsyncClient.find_default_local_api_host()
        if api_host is None:
            return await interaction.followup.send("It seems The AI isn't hosted currently on Bot PC.")
        
        message = await interaction.followup.send("...", wait=True)
        
        full_text = ""
        last_update = time.time()

        async with lms.AsyncClient(api_host) as client:
            model = await client.llm.model("google/gemma-3-1b")

            stream = await model.respond_stream(prompt)

            async for fragment in stream:
                full_text += fragment.content

                if time.time() - last_update > 3:
                    await message.edit(content=full_text)

        return await message.edit(content=full_text)

async def setup(bot):
    await bot.add_cog(ChatbotCog(bot))