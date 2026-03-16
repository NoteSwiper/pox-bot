import time
from typing import Any, Optional, Union
from aiocache import cached
from discord.ext import commands
from discord import DMChannel, Interaction, Message, app_commands

import lmstudio as lms
from sympy import N

from bot import PoxBot
from logger import logger
from stuff import get_lmstudio_token

class ChatbotCog(commands.Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
        self.history = {}
        self.model_id = "liquid/lfm2.5-1.2b"

    group = app_commands.Group(name="ai", description="An AI Chat hosted in local server-")
    
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        content = message.clean_content
        
        if content.strip():
            if content.startswith("p$chat"):
                prompt = content.replace("p$chat", "", 1)
                
                if message.channel:
                    try:
                        channel = message.channel
                        guild = channel.guild
                        if guild:
                            if channel.permissions_for(guild.me).send_messages:
                                async with channel.typing():
                                    api_host = await lms.AsyncClient.find_default_local_api_host()
                                    if not api_host:
                                        api_host = "localhost:1234"
                                    
                                    guild_id = guild.id if not isinstance(channel, DMChannel) else channel.id
                                    
                                    if guild_id not in self.history:
                                        self.history[guild_id] = lms.Chat()
                                    
                                    history: lms.Chat = self.history[guild_id]
                                    history.add_user_message(prompt)
                                    
                                    full = ""
                                    
                                    try:
                                        async with lms.AsyncClient(api_host) as client:
                                            model = await client.llm.model(self.model_id)
                                            stream = await model.respond_stream(prompt)
                                            
                                            async for fragment in stream:
                                                full += fragment.content
                                            
                                            await message.reply(full)
                                            
                                            history.add_assistant_response(full)
                                    except Exception as e:
                                        logger.exception(f"Exception error: {e}")
                                        await message.reply("oh sry I can't respond to you cuz of stupid error")
                    except:
                        pass
    
    @group.command(name="chat", description="Chat with Gemma3-1b")
    async def chat_ai(self, interaction: Interaction, prompt: str):
        await interaction.response.defer()
        api_host = await lms.AsyncClient.find_default_local_api_host()
        if api_host is None:
            return await interaction.followup.send("It seems The AI isn't hosted currently on Bot PC.")
        
        message = await interaction.followup.send("Thinking...", wait=True)

        guild_id = interaction.guild_id or interaction.user.id
        if guild_id not in self.history:
            self.history[guild_id] = lms.Chat()
        
        history: lms.Chat = self.history[guild_id]
        history.add_user_message(prompt)
        
        full_text = ""
        last_update = time.time()

        try:
            token = get_lmstudio_token()
            if not token:
                raise Exception("Couldn't find token info")
            
            async with lms.AsyncClient(api_host) as client:
                model = await client.llm.model(self.model_id)

                stream = await model.respond_stream(prompt)

                async for fragment in stream:
                    full_text += fragment.content

                    if time.time() - last_update > 2.0:
                        if full_text.strip():
                            await message.edit(content=f"{full_text} ▌")
                            last_update = time.time()
                
                await message.edit(content=full_text)

                history.add_assistant_response(full_text)
        except Exception as e:
            logger.exception(f"AI Chat Error: {e}")
            await message.edit(content="Sorry, I encountered an error processing that request.")
    
    @group.command(name="clear_history", description="Clears history.")
    async def clear_history(self, interaction: Interaction):
        await interaction.response.defer()
        
        guild_id = interaction.guild_id or interaction.user.id
        if guild_id in self.history:
            self.history[guild_id] = lms.Chat()
        
        await interaction.followup.send("ok")

async def setup(bot):
    await bot.add_cog(ChatbotCog(bot))