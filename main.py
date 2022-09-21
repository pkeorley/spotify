import time
import datetime
from io import BytesIO

import requests
import disnake
from transliterate import translit
from disnake.ext import commands
from PIL import Image, ImageDraw, ImageFont
from colorthief import ColorThief

from config import configuration


bot = commands.Bot(command_prefix="//", intents=disnake.Intents.all())

class Tools:
	# Перетворити дататайм об'єкт в секунди
	def convert_to_int(self, datatime) -> int:
		return int(round(datatime.timestamp()))


	# Перетворити секунди в дататайм об'єкт
	def convert_to_datetime_minute(self, seconds: int) -> None:
		return datetime.timedelta(seconds=seconds)


	# Транслітеларція тексту
	def transliterate_text(self, text: str) -> str:
		return translit(text, language_code='ru', reversed=True)


	# Маніпуляції з процентами
	def convert_to_precent(self, s: list) -> int:
		return (s[0]*100)/s[1]

	# Перетворення таймстампу пісні в секунди
	def convert_to_seconds(self, arg: str) -> int:
		return int(arg.split(":")[0])*60+int(arg.split(":")[1])


	# Скачати світлину маючи тільки лінк на це зображення
	def download_image_from_url(self, url: str, filepath="photo.png") -> None:
		image = Image.open(BytesIO(requests.get(url).content))
		image.save(filepath)


	# Намалювати текст з вашими настройками
	def draw_text(self, draw_object=None, xy: tuple=(), text: str="None", size: int=10) -> None:
		draw_object.text(
			xy=xy, 
			text=text,
			font=ImageFont.truetype(r'src/fonts/Gotham-Bold.otf', size)
		)


	# Малювати лінію
	def draw_transparent_line(self, image, xy, color, width=1, joint=None) -> None:
	    if len(color) < 4:
	        color += opacity(100)
	    overlay = Image.new('RGBA', image.size, color[:3]+opacity(0))
	    draw = ImageDraw.Draw(overlay)
	    draw.line(xy, color, width, joint)
	    image.alpha_composite(overlay)


	# Накладення транспаренту на ліву сторону зображення
	def impose_a_transparency(self, path, color, gradient_magnitude=2.) -> None:
	    image = Image.open(path)
	    if image.mode != 'RGBA':
	        image = image.convert('RGBA')
	    width, height = image.size
	    gradient = Image.new('L', (width, 1), color=0xFF)
	    for x in range(width):
	        gradient.putpixel((x, 0), int(255 * (1 - gradient_magnitude * float(x) / width)))
	    alpha = gradient.resize(image.size)
	    black_image = Image.new('RGBA', (width, height), color=color)
	    black_image.putalpha(alpha)
	    gradient_image = Image.alpha_composite(image, black_image)
	    gradient_image.save(path)


tools = Tools()
opacity = lambda transparency: (int(255 * (transparency/100.)),)

global spotify
spotify: dict = {}


@bot.command(name="spotify")
async def spotify_(ctx, *, member: disnake.Member=None):
	member = member or ctx.author
	if member.activities:
		for activity in member.activities:
			if isinstance(activity, disnake.Spotify):
				spotify: dict = {
				    "album": activity.album,
				    "album_cover_url": activity.album_cover_url,
				    "artist": activity.artist,
				    "artists": activity.artists,
				    "color": activity.color,
				    "colour": activity.colour,
				    "created_at": activity.created_at,
				    "duration": activity.duration,
				    "end": activity.end,
				    "name": activity.name,
				    "start": activity.start,
				    "title": activity.title,
				    "to_dict": activity.to_dict,
				    "track_id": activity.track_id,
				    "track_url": activity.track_url,
				    "type": activity.type
				}
				break
	else:
		return await ctx.reply("У вас зараз не грає спотіфай.")

	seconds = str(tools.convert_to_datetime_minute(round(time.time())-tools.convert_to_int(spotify["start"])))[2:]
	end = str(spotify["duration"]).split(".")[0][2:]

	tools.download_image_from_url(spotify["album_cover_url"], filepath=configuration["output"] + "icon.png")
	color = ColorThief(configuration["output"] + "icon.png").get_color(quality=1) # Основний колір зображення

	scale = (450, 250, )
	image = Image.new("RGBA", scale, color)
	draw = ImageDraw.Draw(image)

	tools.impose_a_transparency(configuration["output"] + "icon.png", color, 3)
	icon = Image.open(configuration["output"] + "icon.png")
	icon = icon.resize((250, 250))
	image.paste(icon, (scale[0]-250, 0))

	tools.draw_text(draw,
		xy=(16, 15),
		text=spotify["name"],
		size=10
	) # Спотіфай

	tools.draw_text(draw,
		xy=(14, 25),
		text=tools.transliterate_text(spotify["title"]),
		size=35
	) # Назва пісні

	tools.draw_text(draw,
		xy=(16, 65),
		text=tools.transliterate_text(", ".join(spotify["artists"])),
		size=20
	) # Артисти

	tools.draw_transparent_line(image,
		xy=[(10, 210), (440, 210)],
		color=(255, 255, 255)+opacity(50),
		width=4
	) # Перша лінія (транспарент)

	tools.draw_text(draw,
		xy=(20, 217),
		text=seconds,
		size=10
	) # Таймер пінсі (скільки часу вже пройшло)

	tools.draw_text(draw,
		xy=(400, 217),
		text=end,
		size=10
	) # Тривалість пісні

	bar = tools.convert_to_precent([
		tools.convert_to_seconds(seconds),
		tools.convert_to_seconds(end)
	])
	pixeles = (450/100)*round(bar)

	tools.draw_transparent_line(image,
		xy=[(10, 210), (pixeles, 210)],
		color=(255, 255, 255)+opacity(85),
		width=4
	) # Друга лінія

	draw.ellipse(
		xy=[(pixeles, 205), (pixeles+10, 205+10)],
		fill=(255, 255, 255)
	) # Еліпс

	image.save(configuration["output"] + "spotify.png")
	await ctx.reply(file=disnake.File(configuration["output"] + "spotify.png"))


bot.run(configuration["token"])
