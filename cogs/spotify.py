import time
from io import BytesIO

import disnake
import requests
from disnake.ext import commands
from PIL import Image, ImageDraw
from colorthief import ColorThief

from src.modules.tools import Tools, opacity
from config import configuration


class Spotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spotify = {}
        self.tools = Tools()


    @commands.command(name="spotify")
    async def spotify_(self, ctx, *, member: disnake.Member=None):
        member = member or ctx.author
        for activity in member.activities:
            if isinstance(activity, disnake.Spotify):
                self.spotify = {
                    "album_cover_url": activity.album_cover_url,
                    "artists": activity.artists,
                    "duration": activity.duration,
                    "end": activity.end,
                    "name": activity.name,
                    "start": activity.start,
                    "title": activity.title,
                }
                break

        if self.spotify == {}:
            return await ctx.reply("У вас зараз не грає **spotify**")

        async with ctx.channel.typing():
            seconds = str(self.tools.convert_to_datetime_minute(round(time.time())-self.tools.convert_to_int(self.spotify.get("start"))))[2:]
            end = str(self.spotify.get("duration")).split(".")[0][2:]

            icon = BytesIO(requests.get(self.spotify.get("album_cover_url")).content)
            color = ColorThief(icon).get_color(quality=1) # Основний колір зображення
            fill = self.tools.choice_color_text_data(color)

            scale = (450, 150,)
            image = Image.new("RGBA", scale, color)
            draw = ImageDraw.Draw(image)

            icon = Image.open(self.tools.impose_a_transparency(icon, color, 3))
            icon = icon.resize((scale[1], scale[1]))
            image.paste(icon, (scale[0]-scale[1], 0))

            self.tools.draw_text(draw,
                xy=(16, 15),
                text=self.spotify.get("name"),
                size=10,
                fill=fill
            ) # Спотіфай

            self.tools.draw_text(draw,
                xy=(14, 25),
                text=self.tools.transliterate_text(self.spotify.get("title")),
                size=35,
                fill=fill
            ) # Назва пісні

            self.tools.draw_text(draw,
                xy=(16, 65),
                text=self.tools.transliterate_text(", ".join(self.spotify.get("artists"))),
                size=20,
                fill=fill
            ) # Артисти

            self.tools.draw_transparent_line(image,
                xy=[(10, scale[1]-45), (scale[0]-10, scale[1]-45)],
                color=(255, 255, 255)+opacity(50),
                width=4
            ) # Перша лінія (транспарент)

            self.tools.draw_text(draw,
                xy=(20, scale[1]-33),
                text=seconds,
                size=10,
                fill=fill
            ) # Таймер пінсі (скільки часу вже пройшло)

            self.tools.draw_text(draw,
                xy=(scale[0]-50, scale[1]-33),
                text=end,
                size=10,
                fill=fill
            ) # Тривалість пісні

            bar = self.tools.convert_to_precent([
                self.tools.convert_to_seconds(seconds),
                self.tools.convert_to_seconds(end)
            ])
            pixeles = (scale[0]/100)*round(bar)

            self.tools.draw_transparent_line(image,
                xy=[(10, scale[1]-45), (pixeles, scale[1]-45)],
                color=(255, 255, 255)+opacity(85),
                width=4
            ) # Друга лінія

            draw.ellipse(
                xy=[(pixeles, scale[1]-50), (pixeles+10, (scale[1]-50)+10)],
                fill=(255, 255, 255)
            ) # Еліпс

            image.save("spotify.png")
            await ctx.reply(file=disnake.File("spotify.png"))

        
def setup(bot):
    bot.add_cog(Spotify(bot))