import os
import datetime
import calendar
import copy
from typing import Tuple, List

from inspect import getframeinfo, stack

import pygame

def log(*args):
    caller = getframeinfo(stack()[1][0])

    print(f"{caller.filename.split('/')[-1]}:{caller.lineno}", end=" ")
    for arg in args:
        print(arg, end=" ")
    print("")

class Point:
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def get(self) -> Tuple[int, int]:
        return self.x, self.y

    def __add__(self, obj) -> Tuple[int, int]:
        if type(obj) == Point:
            return self.x + obj.x, self.y + obj.y
        elif type(obj) == tuple:
            return self.x + obj[0], self.y + obj[1]
        raise TypeError

    def __repr__(self) -> str:
        return f"<Point '{self.x}' '{self.y}'>"

def save(surf: pygame.Surface, path: str = "./print_me!.png") -> None:
    pygame.image.save(surf, path)
    print(f"Saved to {os.path.abspath(path)}")

def _draw_calendar(surf: pygame.Surface, date: datetime.date, anchor: Point, color, c_radius: int = 40, c_margin: int = 5, c_width: int = 4) -> None:
    first_weekday, num_of_days = calendar.monthrange(date.year, date.month)
    weekday_iter = first_weekday

    today = datetime.date.today()

    log(surf, date, first_weekday, num_of_days, anchor)

    offsets = Point(0, 0)

    next_anchors = Point(0, 0)

    for j in range(weekday_iter):
        offsets.x += c_margin + c_radius * 2 + c_margin + c_width * 2

    for i in range(weekday_iter, num_of_days + 1):
        if today.year == date.year and today.month == date.month and today.day == i:
            pygame.draw.circle(surf, color, offsets + anchor, c_radius // 2, width=c_width)
        pygame.draw.circle(surf, color, offsets + anchor, c_radius, width=c_width)
        log(i, weekday_iter, num_of_days + 1, offsets + anchor)
        offsets.x += c_margin + c_radius * 2 + c_margin + c_width * 2
        weekday_iter += 1
        if weekday_iter > 6:
            offsets.y += c_margin + c_radius * 2 + c_margin + c_width * 2
            offsets.x = 0
            first_weekday = 0
            weekday_iter = 0
        if offsets.x > next_anchors.x:
            next_anchors.x = offsets.x
        if offsets.y > next_anchors.y:
            next_anchors.y = offsets.y

    return next_anchors

def _draw_month(surf: pygame.Surface, font: pygame.font, c_radius: int, c_margin: int, c_width: int, anchor: Point = Point(0, 0), date: datetime.date = None):
    offsets = _draw_calendar(surf, date, anchor, (0, 0, 0), c_radius = c_radius, c_margin = c_margin, c_width = c_width)

    text_surf = font.render(str(date.month), True, (0, 0, 0))
    surf.blit(text_surf, (anchor + (offsets.x // 2 - text_surf.get_rect().right // 2, offsets.y + (c_margin + c_radius * 2 + c_margin + c_width * 2))))

    return offsets

def generate(surf: pygame.Surface, font: pygame.font, anchor: Point = Point(0, 0), scale: Tuple[int, int] = (500, 707), date: datetime.date = None, must_print: int = 6) -> pygame.Surface:
    surf.fill((255, 255, 255))

    text_surf = font.render(f"{date.year} year", True, (0, 0, 0))
    surf.blit(text_surf, (surf.get_rect().center[0] - text_surf.get_rect().right // 2, 0))

    c_radius = 41
    c_margin = 5
    c_width = 6

    offsets = Point(0, 0)

    printed = 0

    initial_anchor = copy.copy(anchor)

    anchor.y = text_surf.get_rect().bottom + (c_margin + c_radius * 2 + c_margin + c_width * 2)

    if date.month > 1:
        offsets = _draw_month(surf, font, c_radius, c_margin, c_width, anchor, datetime.date(date.year, date.month - 1, 1))
        printed += 1
        anchor.x += offsets.x + (c_margin + c_radius * 2 + c_margin + c_width * 2) * 2

    offsets = _draw_month(surf, font, c_radius, c_margin, c_width, anchor, datetime.date(date.year, date.month, 1))
    printed += 1

    for i in range(1, must_print - printed + 1):
        if date.month + i <= 12:
            anchor.x += offsets.x + (c_margin + c_radius * 2 + c_margin + c_width * 2) * 2
            if anchor.x + (c_margin + c_radius * 2 + c_margin + c_width * 2) * 6 > surf.get_width():
                anchor.y += (c_margin + c_radius * 2 + c_margin + c_width * 2) * 8
                anchor.x = initial_anchor.x
            offsets = _draw_month(surf, font, c_radius, c_margin, c_width, anchor, datetime.date(date.year, date.month + i, 1))
            printed += 1

    surf_downscaled = pygame.transform.smoothscale(surf, scale)

    return surf_downscaled

def generate_cheat_sheet(key_cheat_sheet_surface: pygame.Surface, texts: List[str], font: pygame.font, selected: int = 0, selected_color: List[int] = (128, 128, 255), normal_color: List[int] = (255, 255, 255)):
    key_cheat_sheet_surface.fill((33, 33, 33))

    text_surfs = []

    for i, text in enumerate(texts):
        if (i + 1) // 2 == selected:
            color = selected_color
        else:
            color = (255, 255, 255)
        text_surfs.append(font.render(text, True, color))

    for i, text_surf in enumerate(text_surfs):
        if i == 0:
            y_offset = key_cheat_sheet_surface.get_rect().width // 2 - text_surf.get_rect().center[0]
        elif i % 2 == 0:
            y_offset = key_cheat_sheet_surface.get_rect().width - text_surf.get_rect().width
        else:
            y_offset = 2

        key_cheat_sheet_surface.blit(text_surf, (y_offset, ((i + 1) // 2) * text_surf.get_rect().bottom + 6))

def change_index(index, mod, min, max):
    if mod == "-":
        if index - 1 < 0:
            return max - min
        else:
            return index - 1
    elif mod == "+":
        if index + 1 > max:
            return 0
        else:
            return index + 1

def main():
    pygame.init()
    pygame.font.init()

    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((500 + 400, 707))
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 3)

    fonts = [
        "Consolas",
        "CourierNew",
        "DejaVuSansMono",
        "Times",
        "Arial",
        "Helvetica",
        "Courier",
        "Calibri",
        "Skeena",
    ]
    for i, font in enumerate(fonts):
        fonts[i] = [font, pygame.font.match_font(font)]

    tmp_fonts = []
    for i, font in enumerate(fonts):
        if font[1] in tmp_fonts:
            fonts.pop(i)
        else:
            tmp_fonts.append(font[1])
    del tmp_fonts

    if len(fonts) < 1:
        fonts = [None]

    font_index = 0
    font = fonts[font_index]

    font_128 = pygame.font.Font(font[1], 128)
    font_16 = pygame.font.Font(font[1], 16)

    date = datetime.date.today()
    date_desired = [date.year, date.month]

    key_cheat_sheet = pygame.Surface((400, 707))

    must_print = 3

    texts = [
        "Controls and info:",
        "Ctrl+S", "save generated image to file",
        "Horizontal arrows", "Change option",
        "Vertical arrows", "Change betwen options",
        "Font", str(font[0]),
        "Year", str(date.year),
        "Month", str(date.month),
        "Monthes to print", str(must_print)
    ]

    changing_index = 0
    changing_offset = 4

    generate_cheat_sheet(key_cheat_sheet, texts, font_16, selected = changing_index + changing_offset)

    pg_surf = pygame.Surface((2480, 3508))
    vp_surf = generate(surf = pg_surf, font = font_128, anchor = Point(100, 300), date = date, must_print=must_print)

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                break
            elif event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                save(pg_surf)
                generate_cheat_sheet(key_cheat_sheet, texts, font_16, selected = 1)
            elif event.key == pygame.K_LEFT:
                if changing_index == 0:
                    font_index = change_index(font_index, "-", 0, len(fonts) - 1)
                    font = fonts[font_index]
                    texts[changing_offset * 2 + changing_index] = str(font[0])
                    font_128 = pygame.font.Font(font[1], 128)
                    font_16 = pygame.font.Font(font[1], 16)
                    generate_cheat_sheet(key_cheat_sheet, texts, font_16, selected = changing_index + changing_offset)
                    vp_surf = generate(surf = pg_surf, font = font_128, anchor = Point(100, 300), date = date, must_print=must_print)
                elif changing_index == 1:
                    date_desired[0] = date_desired[0] - 1 if date_desired[0] > datetime.MINYEAR else datetime.MINYEAR
                    date = datetime.date(*date_desired, 1)
                    texts[changing_offset * 2 + changing_index + changing_index] = str(date.year)
                    vp_surf = generate(surf = pg_surf, font = font_128, anchor = Point(100, 300), date = date, must_print=must_print)
                    generate_cheat_sheet(key_cheat_sheet, texts, font_16, selected = changing_index + changing_offset)
                elif changing_index == 2:
                    date_desired[1] = date_desired[1] - 1 if date_desired[1] > 1 else 1
                    date = datetime.date(*date_desired, 1)
                    texts[changing_offset * 2 + changing_index + changing_index] = str(date.month)
                    vp_surf = generate(surf = pg_surf, font = font_128, anchor = Point(100, 300), date = date, must_print=must_print)
                    generate_cheat_sheet(key_cheat_sheet, texts, font_16, selected = changing_index + changing_offset)
                elif changing_index == 3:
                    must_print = must_print - 1 if must_print > 1 else 1
                    texts[changing_offset * 2 + changing_index + changing_index] = str(must_print)
                    vp_surf = generate(surf = pg_surf, font = font_128, anchor = Point(100, 300), date = date, must_print=must_print)
                    generate_cheat_sheet(key_cheat_sheet, texts, font_16, selected = changing_index + changing_offset)
            elif event.key == pygame.K_RIGHT:
                if changing_index == 0:
                    font_index = change_index(font_index, "+", 0, len(fonts) - 1)
                    font = fonts[font_index]
                    texts[changing_offset * 2 + changing_index] = str(font[0])
                    font_128 = pygame.font.Font(font[1], 128)
                    font_16 = pygame.font.Font(font[1], 16)
                    generate_cheat_sheet(key_cheat_sheet, texts, font_16, selected = changing_index + changing_offset)
                    vp_surf = generate(surf = pg_surf, font = font_128, anchor = Point(100, 300), date = date, must_print=must_print)
                elif changing_index == 1:
                    date_desired[0] = date_desired[0] + 1 if date_desired[0] < datetime.MAXYEAR else datetime.MAXYEAR
                    date = datetime.date(*date_desired, 1)
                    texts[changing_offset * 2 + changing_index + changing_index] = str(date.year)
                    vp_surf = generate(surf = pg_surf, font = font_128, anchor = Point(100, 300), date = date, must_print=must_print)
                    generate_cheat_sheet(key_cheat_sheet, texts, font_16, selected = changing_index + changing_offset)
                elif changing_index == 2:
                    date_desired[1] = date_desired[1] + 1 if date_desired[1] < 12 else 12
                    date = datetime.date(*date_desired, 1)
                    texts[changing_offset * 2 + changing_index + changing_index] = str(date.month)
                    vp_surf = generate(surf = pg_surf, font = font_128, anchor = Point(100, 300), date = date, must_print=must_print)
                    generate_cheat_sheet(key_cheat_sheet, texts, font_16, selected = changing_index + changing_offset)
                elif changing_index == 3:
                    must_print = must_print + 1 if must_print < 12 else 12
                    texts[changing_offset * 2 + changing_index + changing_index] = str(must_print)
                    vp_surf = generate(surf = pg_surf, font = font_128, anchor = Point(100, 300), date = date, must_print=must_print)
                    generate_cheat_sheet(key_cheat_sheet, texts, font_16, selected = changing_index + changing_offset)
            elif event.key == pygame.K_UP:
                changing_index = change_index(changing_index, "-", 0, (len(texts) - 1) // 2 - changing_offset)
                generate_cheat_sheet(key_cheat_sheet, texts, font_16, selected = changing_index + changing_offset)
            elif event.key == pygame.K_DOWN:
                changing_index = change_index(changing_index, "+", 0, (len(texts) - 1) // 2 - changing_offset)
                generate_cheat_sheet(key_cheat_sheet, texts, font_16, selected = changing_index + changing_offset)
            else:
                generate_cheat_sheet(key_cheat_sheet, texts, font_16, selected = changing_index + changing_offset)

        pygame.display.flip()

        screen.blit(vp_surf, (0, 0))
        screen.blit(key_cheat_sheet, (500, 0))


        clock.tick(144)

    pygame.quit()

if __name__ == "__main__":
    main()
