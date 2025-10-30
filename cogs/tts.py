from io import BytesIO
import sys
from typing import Optional
import discord
import wave
from discord.ext import commands
from discord import app_commands
from edge_tts import Communicate
from gtts import gTTS
from piper import PiperVoice
from logger import logger

voice = PiperVoice.load("./resources/voices/en_US-ryan-high.onnx")

class TTS(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    ttsgroup = app_commands.Group(name="tts",description="Centre of yeah, TTS.")
    
    async def googletts_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        suggestions = []
        
        for code, full in self.bot.gtts_cache_langs.items():
            if current.lower() in code.lower() or current.lower() in full.lower():
                suggestions.append(app_commands.Choice(name=full,value=code))
            
            if len(suggestions) >= 20:
                break
        
        return suggestions
    
    @ttsgroup.command(name="google")
    @app_commands.autocomplete(lang=googletts_autocomplete)
    async def google_text_to_speech(self, interaction: discord.Interaction, text: str, slow: Optional[bool] = False, lang: Optional[str] = "en"):
        await interaction.response.defer(thinking=True)
        
        if lang is None: lang = "en"
        if slow is None: slow = False
        
        abuffer = BytesIO()
        try:
            tts = gTTS(text, lang=lang, slow=slow)
            tts.write_to_fp(abuffer)
            
            abuffer.seek(0)
        except Exception as e:
            await interaction.followup.send(f"An error occured while generating speech: {e}")
            logger.exception(f"{e}")
            return
        
        dfile = discord.File(abuffer, filename="GoogleTTS.mp3")
        
        try:
            await interaction.followup.send(f"Generated. >:D\nType: Google TTS, Input: {text}",file=dfile)
        except Exception as e:
            await interaction.followup.send(f"An error occured while sending speech: {e}")
            logger.exception(f"{e}")
    
    @ttsgroup.command(name="piper")
    async def piper_text_to_speech(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer(thinking=True)
        
        abuffer = BytesIO()
        try:
            with wave.open(abuffer, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(voice.config.sample_rate)
                
                for raw in voice.synthesize(text):
                    wf.writeframes(raw.audio_int16_bytes)
            abuffer.seek(0)
        except Exception as e:
            await interaction.followup.send(f"An error occured while generating speech: {e}")
            logger.exception(f"{e}")
            return
        
        dfile = discord.File(abuffer, filename=f"PiperTTS.mp3")
        
        try:
            await interaction.followup.send(f"Generated. >:D\nType: Piper TTS, Input: {text}",file=dfile)
        except Exception as e:
            await interaction.followup.send(f"An error occured while sending speech: {e}")
            logger.exception(f"{e}")

    @ttsgroup.command(name="edge")
    async def edge_text_to_speech(self, interaction: discord.Interaction, text: str, lang: Optional[str], slow: Optional[bool]):
        if not "edge_tts" in sys.modules:
            logger.error("edge_tts package is not installed in this project. ignoring...")
            await interaction.response.send_message(f"It seems the environment used in discord bot doesn't have `edge_tts` package.")
            return
        
        if not lang:
            lang = "en-US-AndrewMultilingualNeural"
        
        if not slow:
            slow = False
        
        
        await interaction.response.defer(thinking=True)
        
        abuffer = BytesIO()
        try:
            communicate = Communicate(text, lang)
            
            async for chunk in communicate.stream():
                self.bot.received_chunks += 1
                if chunk["type"] == "audio":
                    abuffer.write(chunk["data"])
            
            abuffer.seek(0)
        except Exception as e:
            await interaction.followup.send(f"An error occured while generating speech: {e}")
            logger.exception(f"{e}")
            return
        
        dfile = discord.File(abuffer, filename="EdgeTTS.mp3")
        
        try:
            await interaction.followup.send(f"Genarated. >:D\nType: Edge TTS, Input: {text}",file=dfile)
        except Exception as e:
            await interaction.followup.send(f"An error occured while sending speech: {e}")
            logger.exception(f"{e}")

async def setup(bot):
    await bot.add_cog(TTS(bot))