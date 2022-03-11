import pathlib
import random
from pathlib import Path

from skimage import io
import numpy as np


def create_blank_image(width=1000, height=1000):
    return np.zeros(shape=(width, height), dtype=np.uint8)


def draw_rectangle(img, start: tuple, end: tuple, color: tuple):
    for i in range(start[0], end[0]):
        for j in range(start[1], end[1]):
            img[i, j, :] = np.array(color)


def draw_rectangle_delta(img, start: tuple, delta: int, color: tuple):
    draw_rectangle(img, start, (start[0] + delta, start[1] + delta), color)


def hex2rgb(hex_str: str) -> tuple:
    """
    Converts HEX format to RGB
    :param hex_str:
    :return: tuple(r, g, b)
    """
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(rgb: tuple) -> str:
    """
    Converts RGB tuple format to HEX string
    :param rgb:
    :return: hex string
    """
    return '#%02x%02x%02x' % rgb


# RGB
COLORS = {
    "Абрикосовый": (251, 206, 177),  # Абрикосовый
    "Абрикосовый Крайола": (253, 217, 181),  # Абрикосовый Крайола
    "Агатовый серый": (181, 184, 177),  # Агатовый серый
    "Аквамариновый": (127, 255, 212),  # Аквамариновый
    "Аквамариновый Крайола": (120, 219, 226),  # Аквамариновый Крайола
    "Ализариновый красный": (227, 38, 54),  # Ализариновый красный
    "Алый": (255, 36, 0),  # Алый
    "Амарантово-пурпурный": (171, 39, 79),
    "Амарантово-розовый": (241, 156, 187),
    "Амарантовый": (229, 43, 80),
    "Амарантовый глубоко-пурпурный": (159, 43, 104),
    "Амарантовый маджента": (237, 60, 202),
    "Амарантовый светло-вишневый": (205, 38, 130),
    "Американский розовый": (255, 3, 62),
    "Аметистовый": (153, 102, 204),
    "Античная латунь": (205, 149, 117),
    "Антрацитово-серый": (41, 49, 51),
    "Антрацитовый": (70, 68, 81),
    "Арлекин": (68, 148, 74),
    "Аспидно-синий": (106, 90, 205),
    "Бабушкины яблоки": (168, 228, 160)
    # ...
}

PALETTES = {
    "Розовый и изюм": ['e52165', '0d1137'],
    "Красный, морской пены, нефрита и фиалки": ['d72631', 'a2d5c6',
                                                '077b8a', '5c3c92'],
    "Желтый, пурпурный, голубой, черный": ['e2d810', 'd9138a',
                                           '12a4d9', '322e2f'],
    "Горчица и черный": ['f3ca20', '000000'],
    "Пурпурный, золотарник, бирюза и кирпич": ['cf1578', '38d21d',
                                               '039fbe', 'b20238'],
    "Оттенки розового и коричневого": ['e75874', 'be1558',
                                       'fbcbc9', '322514'],
    "Золото, уголь и серый": ['ef9d10f', '3b4d61', '6b7b8c'],
    "Военно-морской флот, миндаль, красно-оранжевый и манго": ['1e3d59', 'f5f0e1',
                                                               'ff6e40', 'ffc13b'],
    "Загар, глубокий бирюзовый и черный": ['ecc19c', '1e847f', '000000'],
    "Военно-морской флот, охра, сожженная сиена и светло-серый": ['26495c', 'c4a35a',
                                                                  'c66b3d', 'e5e5dc'],
    "Сиреневый, сапфировый и пудрово-серый": ['d9a6b3', '1868ae', 'c6d7eb'],
    "Синий, бордовый и индиго": ['408ec6', '7a2048', '1e2761'],
    "Малина и оттенки синего": ['8a307f', '79a7d3', '6883bc'],
    "Глубокий сосново-зеленый, оранжевый и светло-персиковый": ['1d3c45', 'd2601a', 'fff1e1'],
    "Морская пена, лосось и флот": ['aed6dc', 'ff9a8d', '4a536b'],
    "Руж, зеленый и пурпурный": ['da68a0', '77c593', 'ed3572'],
    "Чирок, коралл, бирюза и серый": ['316879', 'f47a60', '7fe7dc', 'ced7d8'],
    "Фуксия, сепия, ярко-розовый и темно-фиолетовый": ['d902ee', 'ffd79d', 'f162ff', '320d3e'],
    "Светло-розовый, шалфей, голубой и виноград": ['ffcce7', 'daf2dc', '81b7d2', '4d5198'],
    "Бежевый, черно-коричневый и желто-коричневый": ['ddc3a5', '201e20', 'e0a96d'],
    "Сепия, чирок, беж и шалфей": ['edca82', '097770', 'e0cdbe', 'a9c0a6'],
    "Желто-зеленый, оливковый и лесной зеленый": ['e1dd72', 'a8c66c', '1b6535'],
    "Фуксия, желтый и пурпурный": ['d13ca4', 'ffea04', 'fe3a9e'],
    "Горчица, шалфей и зеленый лес": ['e3b448', 'cbd18f', '3a6b35'],
    "Бежевый, шифер и хаки": ['f6ead4', 'a2a595', 'b4a284'],
    "Бирюзовый и фиолетовый": ['79cbb8', '500472'],
    "Светло-розовый, зеленый и морской пены": ['f5beb4', '9bc472', 'cbf6db'],
    "Алый, светло-оливковый и светло-бирюзовый": ['b85042', 'e7e8d1', 'a7beae'],
    "Красный, желтый, голубой и ярко-фиолетовый": ['d71b3b', 'e8d71e', '16acea', '4203c9'],
    "Оливковое, бежевое и коричневое": ['829079', 'ede6b9', 'b9925e'],
    "Оттенки синего и зеленого": ['1fbfb8', '05716c', '1978a5', '031163'],
    "Бирюзовый, горчичный и черный": ['7fc3c0', 'cfb845', '141414'],
    "Персик, лосось и чирок": ['efb5a3', 'f57e7e', '315f72']
}


async def process(img_name: str, rectangle_color: tuple = (255, 255, 255), random_color: bool = False,
            palette_name: str = None,
            random_palette: bool = False) -> (Path, str):
    img = io.imread(img_name)
    count_dots_hor = 10
    count_dots_vert = 10
    delta_row = img.shape[0] / count_dots_hor
    delta_column = img.shape[1] / count_dots_vert
    width_square = int(min(delta_row * 0.75, delta_column * 0.75))
    # for j in range(3):
    #     for i in range(img.shape[1] // 2):
    #         img[:, i * j % img.shape[1]] = img[:, i + img.shape[1] // 2]
    palette_key, color_key = None, None
    if random_color:
        color_key = random.choice(list(set(COLORS.keys())))
        colors = [COLORS[color_key]]
    elif palette_name:
        palette_key = palette_name
        colors = [hex2rgb(color) for color in PALETTES[palette_key]]
    elif random_palette:
        palette_key = random.choice(list(set(PALETTES.keys())))
        colors = [hex2rgb(color) for color in PALETTES[palette_key]]
    else:
        colors = [rectangle_color]
    for i in range(count_dots_hor):
        for j in range(count_dots_vert):
            if random.random() > 0.5:
                draw_rectangle_delta(img,
                                     (int(i * delta_row), int(j * delta_column)),
                                     width_square, color=random.choice(colors))
    fname = f'{img_name[:-4]}_output.jpg'
    io.imsave(fname, img)
    return fname, palette_key if palette_key else (color_key if color_key else "")
