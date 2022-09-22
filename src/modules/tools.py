import datetime
from io import BytesIO

import disnake
import requests
from transliterate import translit
from PIL import Image, ImageDraw, ImageFont


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
    def draw_text(self, draw_object=None, xy: tuple=(), text: str="None", size: int=10, fill=(255, 255, 255), path=r"src/fonts/Gotham-Bold.otf") -> None:
        draw_object.text(
            xy=xy, 
            text=text,
            font=ImageFont.truetype(path, size),
            fill=fill if isinstance(fill, str) else str(disnake.Color.from_rgb(fill[0], fill[1], fill[2]))
        )

    # Перетворення HEX на RGB
    def hex_to_rgb(self, value: str) -> tuple:
        value = value.lstrip('#')
        return tuple(int(value[i:i + len(value) // 3], 16) for i in range(0, len(value), len(value) // 3))


    # Выбрать цвет текста с помощью RGB
    def choice_color_text_data(self, rgb: tuple) -> tuple:
        sa = (rgb[0]+rgb[1]+rgb[2])/3
        if sa >= 128: return (40, 40, 40)
        else: return (255, 255, 255)


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


opacity = lambda transparency: (int(255 * (transparency/100.)),)