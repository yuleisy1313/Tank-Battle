"""
    Yuleisy Carmona Vasquez
    22-SISN-2-016
"""

from pathlib import Path
import pygame as pg
from enum import Enum
import pygame_menu as pg_menu

# Inicializar pygame
pg.display.init()


class Direction(Enum):
    FRONT = 1
    BACK = 2
    LEFT = 3
    RIGHT = 4


class CONSTANTES(Enum):
    '''
    Todas las constantes utilizadas en el juego
    '''

    # * Paths
    ROOT_PATH = Path(__file__).parent.parent
    ROOT_STR_PATH = str(Path(__file__).parent.parent)

    # * Constantes de ventana
    FPS = 60.0
    WINDOW_SCALE = 1.00
    TILE_SIZE = int(pg.display.Info().current_h * 0.06)
    WINDOW_SIZE = (13 * TILE_SIZE, 13 * TILE_SIZE)

    # * Colores específicos del menú
    MENU_TITLE_COLOR = (0, 128, 0)
    MENU_BACKGROUND_COLOR = (0, 0, 0)
    TRANSPARENT_COLOR = (0, 0, 0, 0)

    # * Constantes de colores básicos
    COLOR_WHITE = (255, 255, 255)
    COLOR_GREEN = (0, 255, 0)
    COLOR_BLACK = (0, 0, 0)
    COLOR_RED = (255, 0, 0)

    # * Constantes de fuentes
    MENU_FONT = pg_menu.font.FONT_DIGITAL
    MENU_FONT_SIZE = int(TILE_SIZE * 0.7)

    # * Extras
    ASSETS_PATH = ROOT_PATH / 'Assets'
