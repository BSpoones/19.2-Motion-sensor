
from discord.ext import commands
from discord.ext.commands import Bot as BotBase
from discord import Embed, Intents
import asyncio, os, discord
from discord.ext.commands.context import Context
from discord.ext.commands import Cog, command
token = "OTc4NzQwNDMzMTAwMzQ1MzQ0.GlKDBK.gddSHvnw9qd657R2zMqUvrRYCRAIGtRk8IsEAA"

class Bot(BotBase):
    """
    The main body of the bot
    """
    def __init__(self):
        self.TOKEN = token
        self.ready = False


        super().__init__(
            command_prefix=".",
            intents=Intents.all()
            )

    def run(self):
        super().run(self.TOKEN, reconnect=True)

    async def on_ready(self):
        if not self.ready:
            self.ready = True
        print("I AM READY")
    async def process_commands(self, message):
        ctx = await self.get_context(message,cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if not self.ready:
                await ctx.send("I am still starting up, try again in a few seconds")
            else:
                await self.invoke(ctx)
    
    async def on_message(self, message) -> str:
        if not message.author.bot:
            if str(message.content) == ".exit":
                os._exit(1)
    
    def send_message(self,message=None,embed=None):
        output_channel = self.get_channel(978740800315883583)
        if embed is None:
            self.loop.create_task(output_channel.send(message))
        else:
            self.loop.create_task(output_channel.send(embed=embed))
            
    
    def set_presence(self, armed: bool):
        if armed:
            armed = "ARMED"
        else:
            armed = "DISARMED"
        self.loop.create_task(self.change_presence(
            status=discord.Status.do_not_disturb, 
            activity=discord.Activity(
                type=discord.ActivityType.playing, 
                name=(f"I am {armed}")
                )
            )
        )

bot = Bot()

