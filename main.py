import os

import disnake
from disnake.ext import commands

from config import configuration


bot = commands.Bot(command_prefix=".", intents=disnake.Intents.all())


@bot.event
async def on_ready():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            try:
                bot.load_extension(f"cogs.{filename[:-3]}")
            except Exception as error:
                print("[*] " + configuration["errors"]["failed_load_cog"].replace("$filename", filename))
    print("[*] " + configuration.get("events").get("on_ready"))


bot.run(configuration.get("token"))
