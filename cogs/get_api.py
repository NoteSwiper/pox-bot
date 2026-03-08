from aiocache import cached
from discord import Embed, Interaction, app_commands
from discord.ext import commands

from mcstatus import JavaServer
import mojang

from roblox import UserNotFound
import roblox
import roblox.users
from roblox.utilities.exceptions import Forbidden, BadRequest, TooManyRequests, InternalServerError, NotFound

from bot import PoxBot

class GetAPI(commands.Cog):
    def __init__(self, bot: PoxBot):
        self.bot: PoxBot = bot
    
    minecraft_group = app_commands.Group(name="minecraft", description="Sub-group")
    roblox_group = app_commands.Group(name="roblox", description="Sub-group")
    
    @cached(60)
    @minecraft_group.command(name="server_lookup", description="Lookups minecraft server.")
    async def minecraft_server_lookup(self, interaction: Interaction, address: str):
        await interaction.response.defer()
        embed = Embed(title=f"Lookup for \"{address}\"")
        
        try:
            row_to_add = {}
            server = await JavaServer.async_lookup(address)
            
            status = await server.async_status()
            embed.description = status.motd.to_plain()
            row_to_add = {
                "Version": status.version.name,
                "Protocol Version": status.version.protocol,
                "Latency": f"{status.latency:2f} ms",
                "Players": f"{status.players.online}/{status.players.max}"
            }
            
            try:
                query = server.query()
                
                if query.motd:
                    embed.description = query.motd.to_plain()
                
                if query.players and query.players.list:
                    row_to_add["Player list"] = ', '.join(query.players.list)
            except Exception:
                if status.players.sample:
                    names = [p.name for p in status.players.sample]
                    row_to_add["Player list"] = ', '.join(names)
                else:
                    row_to_add["Player list"] = "Not available"
            
            for key, value in row_to_add.items():
                embed.add_field(name=key, value=value)
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            return await interaction.followup.send(f"Failed to lookup minecraft server for \"{address}\": {e}")

    @cached(300)
    @minecraft_group.command(name="username_to_uuid", description="Converts Username to UUID.")
    async def username_to_uuid(self, interaction: Interaction, username: str):
        cached = self.bot.cache.get(f"mcid_{username}")
        if cached:
            await interaction.response.send_message(cached)
        else:
            cached = mojang.get_uuid(username)
            
            if cached:
                self.bot.cache.set(f"mcid_{username}",cached)
                await interaction.response.send_message(cached)
            else:
                await interaction.response.send_message("Couldn't resolve the username.")
    
    @cached(300)
    @minecraft_group.command(name="uuid_to_username", description="Converts UUID to Username.")
    async def uuid_to_username(self, interaction: Interaction, uuid: str):
        cached = self.bot.cache.get(f"mcuuid_{uuid}")
        if cached:
            await interaction.response.send_message(cached)
        else:
            cached = mojang.get_username(uuid)
            
            if cached:
                self.bot.cache.set(f"mcuuid_{uuid}",cached)
                await interaction.response.send_message(cached)
            else:
                await interaction.response.send_message("Couldn't resolve the UUID.")
    
    # auto complete for roblox usernames
    async def roblox_username_autocomplete(self, interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
        choices = []
        try:
            async for user in self.bot.roblox_client.user_search(current, max_items=10):
                choices.append(app_commands.Choice(name=f"{user.display_name} (@{user.name})", value=user.name))
                if len(choices) >= 24:
                    break
        except Exception:
            pass
        return choices
    
    @cached(300)
    @roblox_group.command(name="avatar", description="Get Roblox user avatar by username.")
    @app_commands.autocomplete(username=roblox_username_autocomplete)
    async def roblox_get_avatar(self, interaction: Interaction, username: str):
        await interaction.response.defer(thinking=True)
        avatar_cache = self.bot.cache.get(f"rbxthumb_user_avatar_{username}")

        if avatar_cache:
            avatar_url = avatar_cache
        else:
            try:
                user = await self.bot.roblox_client.get_user_by_username(username)
                if not user:
                    return await interaction.followup.send(f"User '{username}' not found.")
                
                thumb = await self.bot.roblox_client.thumbnails.get_user_avatar_thumbnails(
                    users=[user.id],
                    type=roblox.thumbnails.AvatarThumbnailType.full_body,
                    size=(420, 420)
                )

                if len(thumb) > 0:
                    avatar_url = thumb[0]
                    self.bot.cache.set(f"rbxthumb_user_avatar_{username}", avatar_url)
                else:
                    avatar_url = None
            except UserNotFound:
                return await interaction.followup.send(f"User '{username}' not found.")
            except BadRequest:
                return await interaction.followup.send("API returned Error 403 Bad Request.")
            except Forbidden:
                return await interaction.followup.send(f"User '{username}' could be banned or hidden.")
            except TooManyRequests:
                return await interaction.followup.send("API rate limit exceeded. Please try again later.")
            except InternalServerError:
                return await interaction.followup.send("The roblox API is currently outaged.")
            except Exception as e:
                return await interaction.followup.send(f"An unexpected error occurred: {e}")
            
        if avatar_url:
            embed = Embed(title=f"Avatar for '{username}'")
            embed.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.display_avatar.url
            )
            embed.set_image(url=avatar_url.image_url)
            return await interaction.followup.send(embed=embed)
        else:
            return await interaction.followup.send(f"Failed to retrieve avatar for '{username}'.")

    @cached(300)
    @roblox_group.command(name="user", description="Get Roblox user info by username.")
    @app_commands.autocomplete(username=roblox_username_autocomplete)
    async def roblox_get_user(self, interaction: Interaction, username: str):
        await interaction.response.defer(thinking=True)
        info_cache = self.bot.cache.get(f"rbxuser_{username}")
        image_cache = self.bot.cache.get(f"rbxthumb_user_avatar_{username}")

        result = None
        image_url = None

        if info_cache:
            result = info_cache
        else:
            try:
                user = await self.bot.roblox_client.get_user_by_username(username)
                if user:
                    result = user
                    self.bot.cache.set(f"rbxuser_{username}", result)
                else:
                    return await interaction.followup.send(f"User '{username}' not found.")
            except UserNotFound:
                return await interaction.followup.send(f"User '{username}' not found.")
            except BadRequest:
                return await interaction.followup.send("API returned Error 403 Bad Request.")
            except Forbidden:
                return await interaction.followup.send(f"User '{username}' could be banned or hidden.")
            except TooManyRequests:
                return await interaction.followup.send("API rate limit exceeded. Please try again later.")
            except InternalServerError:
                return await interaction.followup.send("The roblox API is currently outaged.")
            except Exception as e:
                return await interaction.followup.send(f"An unexpected error occurred: {e}")
        
        if image_cache:
            image_url = image_cache
        else:
            try:
                thumb = await self.bot.roblox_client.thumbnails.get_user_avatar_thumbnails(
                    users=[result.id],
                    type=roblox.thumbnails.AvatarThumbnailType.full_body,
                    size=(420, 420)
                )

                if len(thumb) > 0:
                    image_url = thumb[0]
                    self.bot.cache.set(f"rbxthumb_user_avatar_{username}", image_url)
                else:
                    image_url = None
            except Exception:
                image_url = None

        if result:
            if isinstance(result, roblox.users.User):
                embed = Embed(title=f"Information for '{result.name}'", description=result.description)
                embed.add_field(name="User ID", value=result.id, inline=True)
                embed.add_field(name="Username", value=result.name, inline=True)
                embed.add_field(name="Display Name", value=result.display_name, inline=True)
                embed.add_field(name="Banned", value="Yes" if result.is_banned else "No", inline=True)
                embed.add_field(name="Created", value=result.created.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=True)

                if image_url:
                    embed.set_thumbnail(url=image_url.image_url)

                return await interaction.followup.send(embed=embed)
        else:
            return await interaction.followup.send("Failed to retrieve user information.")
async def setup(bot):
    await bot.add_cog(GetAPI(bot))