import os
import subprocess
import uuid
import time
import discord

from datetime import datetime, UTC
from discord.ext import commands
from discord import Forbidden, HTTPException, Interaction, MissingApplicationID, app_commands

import stuff
stuff.create_dir_if_not_exists("./logs")

#import help_command
from bot import PoxBot

from logger import logger

handled_messages = 0
current_guild = 0

start_time = time.time()

commit_hash = ""

try:
    output = subprocess.run(['git','rev-parse','--short','HEAD'], capture_output=True, text=True, check=True)
    commit_hash = output.stdout.strip()
except subprocess.CalledProcessError as e:
    logger.error(f"Error occured: {e}")
except FileNotFoundError:
    logger.error("Git command not found. make sure to check if Git is installed.")

bot_token = stuff.get_bot_token()

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

INACTIVITY_THRESHOLD = 300

bot = PoxBot(
    intents=intents,
    command_prefix=commands.when_mentioned_or("pox!"),
    owner_id=1321324137850994758,
    #chunk_guilds_at_startup=False,
    #member_cache_flags=discord.MemberCacheFlags.none()
)

tree = bot.tree


@app_commands.command(name="reload_cogs", description="Reloads cogs. (not restarting bot)")
@commands.is_owner()
async def reload_cogs(interaction: Interaction):
    await interaction.response.defer()
    for fname in os.listdir('./cogs'):
        if fname.endswith('.py'):
            logger.debug(f"Loading extension {fname[:-3]}.")
            
            try:
                await bot.reload_extension(f"cogs.{fname[:-3]}")
                logger.debug(f"Successfully loaded {fname[:-3]}.")
            except commands.ExtensionNotLoaded as e:
                logger.exception(f"Extension {fname[:-3]} was not loaded due to {e}.")
            except commands.ExtensionNotFound:
                logger.exception(f"Extension {fname[:-3]} was not found from cogs folder.")
            except commands.NoEntryPointError:
                logger.exception(f"Extension {fname[:-3]} has no entrypoint to load.")
            except commands.ExtensionFailed as e:
                logger.exception(f"Extension {fname[:-3]} has failed to load due to {e}.")
            except Exception as e:
                logger.exception(f"Uncaught exception thrown while reloading, due to {e}.")
    
    try:
        await bot.tree.sync()
    except app_commands.CommandSyncFailure:
        logger.exception("CommandSyncFailure: Invalid command data")
        return await interaction.followup.send("Failed to sync commands. It seems some commands has invalid data.")
    except Forbidden:
        logger.error("Forbidden: The bot doesn't have permission to use `application.commands`")
        #await interaction.followup.send("Failed to sync commands. The scope `application.commands` is not allowed in this guild.\nMake sure to allow the usage of `application.commands`.")
        return
    except MissingApplicationID:
        logger.error("MissingApplicationID: The application ID is empty or missing")
        return
    except app_commands.TranslationError:
        logger.exception("TranslationError: Error occured while translating commands")
        return await interaction.followup.send("Failed to sync commands. It seems the syncing failed due to translation failure.")
    except HTTPException:
        logger.error("HTTPException: Failed to sync commands")
        return await interaction.followup.send("Failed to sync commands.")
    
    return await interaction.followup.send("Successfully reloaded cogs and synchronized commands to discord.")

session_uuid = uuid.uuid4()

last_interaction = datetime.now(UTC)

namesignature = stuff.generate_namesignature()
last_commit_message = stuff.get_latest_commit_message()

if __name__ == "__main__":
    if not bot_token:
        print("You should to put the bot token to 'TOKEN' in .env!")
        exit()
    else:
        try:
            bot.run(bot_token, log_handler=None)
        except KeyboardInterrupt:
            print("Shutting down...")
            pass
        finally:
            print("Bot has been stopped")