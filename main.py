import stuff
stuff.create_dir_if_not_exists("./logs")

import os
import discord

from datetime import UTC
from discord.ext import commands
from discord import Forbidden, HTTPException, Interaction, MissingApplicationID, app_commands

from bot import PoxBot
from logger import logger

bot_token = stuff.get_bot_token()

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

bot = PoxBot(
    intents=intents,
    command_prefix=commands.when_mentioned_or("p!"),
    owner_id=457436960655409153,
    #chunk_guilds_at_startup=False,
    #member_cache_flags=discord.MemberCacheFlags.none()
)

tree = bot.tree

@tree.command(name="reload_cogs", description="Reloads cogs. (not restarting bot)")
@app_commands.check(stuff.is_bot_owner)
async def reload_cogs(interaction: Interaction):
    loaded_extension = 0
    failed_extension = 0
    await interaction.response.defer()
    for fname in os.listdir('./cogs'):
        if fname.endswith('.py'):
            logger.debug(f"Loading extension {fname[:-3]}.")

            if fname[:-3] in bot.EXCLUDE_EXTENSIONS:
                logger.warning("This extension has excluded from loading.")
                continue
            
            try:
                await bot.reload_extension(f"cogs.{fname[:-3]}")
                logger.debug(f"Successfully loaded {fname[:-3]}.")
                loaded_extension += 1
            except commands.ExtensionNotLoaded as e:
                logger.exception(f"Extension {fname[:-3]} was not loaded due to {e}.")
                failed_extension += 1
            except commands.ExtensionNotFound:
                logger.exception(f"Extension {fname[:-3]} was not found from cogs folder.")
                failed_extension += 1
            except commands.NoEntryPointError:
                logger.exception(f"Extension {fname[:-3]} has no entrypoint to load.")
                failed_extension += 1
            except commands.ExtensionFailed as e:
                logger.exception(f"Extension {fname[:-3]} has failed to load due to {e}.")
                failed_extension += 1
            except Exception as e:
                logger.exception(f"Uncaught exception thrown while reloading, due to {e}.")
                failed_extension += 1
    
    try:
        synched = await bot.tree.sync()
        logger.info(f"Synchronized {len(synched)} commands, with {loaded_extension} loaded extensions and {failed_extension} failed.")
        return await interaction.followup.send(f"Synchronized {len(synched)} commands, with {loaded_extension} loaded extensions and {failed_extension} failed.")
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

@tree.error
async def on_app_command_error(interaction: Interaction, error: app_commands.AppCommandError) -> None:
    if isinstance(error, app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandInvokeError):
            logger.exception(f"An error occurred while invoking command: {error}")
            await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)
            return
        elif isinstance(error, app_commands.TransformerError):
            logger.exception(f"An error occurred during argument transformation: {error}")
            await interaction.response.send_message("An error occurred while processing command arguments.", ephemeral=True)
            return
        elif isinstance(error, app_commands.TranslationError):
            logger.exception(f"An error occurred during command translation: {error}")
            await interaction.response.send_message("An error occurred while translating the command.", ephemeral=True)
            return
        elif isinstance(error, app_commands.CheckFailure):
            if isinstance(error, app_commands.NoPrivateMessage):
                logger.warning(f"Check failure: {error}")
                await interaction.response.send_message("This command cannot be used in private messages.", ephemeral=True)
                return
            elif isinstance(error, app_commands.MissingRole):
                logger.warning(f"Check failure: {error}")
                await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
                return
            elif isinstance(error, app_commands.MissingAnyRole):
                logger.warning(f"Check failure: {error}")
                await interaction.response.send_message("You do not have any of the required roles to use this command.", ephemeral=True)
                return
            elif isinstance(error, app_commands.MissingPermissions):
                logger.warning(f"Check failure: {error}")
                await interaction.response.send_message("You do not have the required permissions to use this command.", ephemeral=True)
                return
            elif isinstance(error, app_commands.BotMissingPermissions):
                logger.warning(f"Check failure: {error}")
                await interaction.response.send_message("I do not have the required permissions to execute this command.", ephemeral=True)
                return
            elif isinstance(error, app_commands.CommandOnCooldown):
                logger.warning(f"Check failure: {error}")
                await interaction.response.send_message(f"This command is on cooldown. Please try again after {round(error.retry_after, 2)} seconds.", ephemeral=True)
                return
            else:
                logger.warning(f"Check failure: {error}")
                await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
                return
        elif isinstance(error, app_commands.CommandLimitReached):
            logger.warning(f"Command limit reached: {error}")
            await interaction.response.send_message("The command limit has been reached. Please try again later.", ephemeral=True)
            return
        elif isinstance(error, app_commands.CommandAlreadyRegistered):
            logger.warning(f"Command already registered: {error}")
            await interaction.response.send_message("This command is already registered.", ephemeral=True)
            return
        elif isinstance(error, app_commands.CommandSignatureMismatch):
            logger.warning(f"Command signature mismatch: {error}")
            await interaction.response.send_message("There is a signature mismatch for this command.", ephemeral=True)
            return
        elif isinstance(error, app_commands.CommandNotFound):
            logger.warning(f"Command not found: {error}")
            await interaction.response.send_message("This command was not found.", ephemeral=True)
            return
        elif isinstance(error, app_commands.CommandSyncFailure):
            logger.warning(f"Command sync failure: {error}")
            await interaction.response.send_message("Failed to synchronize commands.", ephemeral=True)
            return
        else:
            logger.exception(f"An unknown AppCommandError occurred: {error}")
            await interaction.response.send_message("An unknown error occurred while executing the command.", ephemeral=True)
            return
    else:
        logger.exception(f"An unexpected error occurred: {error}")
        return

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