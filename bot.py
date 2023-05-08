import time
import discord
from discord.ext import commands
from servers import SteamServerBrowser

STEAM_APPID = '70'
STEAM_API_KEY = '...'
DISCORD_TOKEN = '...'
FREQUENCY = int(30)

class SteamGameServerView(discord.ui.View):
    def __init__(self, ctx=None):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.messages = {}
        self.lastInteractionTime = None
        self.serverBrowser = SteamServerBrowser(STEAM_API_KEY, STEAM_APPID)

    async def sendMessage(self, server):
        if server.address in self.messages: # Edit if the address already was listed
            await self.messages[server.address].edit(content=str(server), suppress=True)
        else: # Add new entry
            self.messages[server.address] = await self.ctx.send(content=str(server), suppress_embeds=True)

    async def removeMessage(self, address):
        entry = self.messages.get(address, None)
        if entry is None:
            return
        
        await entry.delete()
        del self.messages[address]

    async def clearMessages(self):
        for _, v in self.messages.items():
            await v.delete()
        self.messages = {}

    @discord.ui.button(label='Refresh', style=discord.ButtonStyle.green, custom_id='persistence:refresh')
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer() # We do not respond with an actual message

        currentTime = int(time.time()) # Simple "rate" limit
        if self.lastInteractionTime and (currentTime < (self.lastInteractionTime + FREQUENCY)):
            return
        self.lastInteractionTime = currentTime

        items = self.serverBrowser.get()
        if len(items) == 0:
            await self.clearMessages() # No more servers to show, clear all listing messages
            return
        
        keys = set([server.address for server in items])
        for messageToRemove in [k for k, _ in self.messages.items() if k not in keys]:
            await self.removeMessage(messageToRemove) # Remove dead/stale servers, if any

        for server in items:
            await self.sendMessage(server) # Send/Edit server listing message

class SteamGameServerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='/', intents=intents)

    async def setup_hook(self):
        self.add_view(SteamGameServerView())

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

BOT = SteamGameServerBot()

@BOT.command()
@commands.is_owner()
async def servers(ctx: commands.Context):
    await ctx.send("MS:R Server List", view=SteamGameServerView(ctx))

BOT.run(DISCORD_TOKEN)