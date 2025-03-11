"""
    Yuleisy Carmona Vasquez
    22-SISN-2-016
"""

from enum import Enum
from Utilidades.Constantes import CONSTANTES


class ASSETS(Enum):
    '''
    Todas las constantes de los assets utilizados en el juego
    '''

    # Referencia al directorio de assets
    ASSETS_DIR = CONSTANTES.ASSETS_PATH.value

    # * Imagenes
    MENU_BACKGROUND = ASSETS_DIR / "image" / "Backgrounds" / "War4" / "000.png"
    GAME_BACKGROUND = ASSETS_DIR / "image" / "Tileset" / \
        "Tile_01.png"  # New variable for the other screen

    # * Musica
    BACKGROUND_MUSIC = ASSETS_DIR / "sounds" / "background.mp3"
    FIRE_SOUND = ASSETS_DIR / "sounds" / "fire.ogg"
    CLICK_SOUND = ASSETS_DIR / "sounds" / "click_menu_effect.mp3"
    LOSE_MUSIC = ASSETS_DIR / "sounds" / "gameover.ogg"
    GAME_START_MUSIC = ASSETS_DIR / "sounds" / "gamestart.ogg"
    VICTORY_MUSIC = ASSETS_DIR / "sounds" / "gamestart.ogg"

    # * Sprites
    # ? Personaje
    TANK_SPRITE_UP = ASSETS_DIR / "image" / "Personaje" / "tank_up.png"
    TANK_SPRITE_DOWN = ASSETS_DIR / "image" / "Personaje" / "tank_down.png"
    TANK_SPRITE_LEFT = ASSETS_DIR / "image" / "Personaje" / "tank_left.png"
    TANK_SPRITE_RIGHT = ASSETS_DIR / "image" / "Personaje" / "tank_right.png"
    

    # PLAYER_SPRITE = ASSETS_DIR / "sprites" / "player.png"
    # # ? Enemigos
    ENEMY_SPRITE_RIGHT = ASSETS_DIR / "image" / "Enemy" / "enemy-tank-pointing-right.png"
    ENEMY_SPRITE_LEFT = ASSETS_DIR / "image" / "Enemy" / "enemy-tank-pointing-left.png"
    ENEMY_SPRITE_UP = ASSETS_DIR / "image" / "Enemy" / "enemy-tank-pointing-up.png"
    ENEMY_SPRITE_DOWN = ASSETS_DIR / "image" / "Enemy" / "enemy-tank-pointing-down.png"

    # ? Enemigo@ suicida
    SUICIDE_ENEMY_SPRITE_RIGHT = ASSETS_DIR / "image" / "Enemy" / "suicide-tank-right.png"
    SUICIDE_ENEMY_SPRITE_LEFT = ASSETS_DIR / "image" / "Enemy" / "suicide-tank-left.png"
    SUICIDE_ENEMY_SPRITE_DOWN = ASSETS_DIR / "image" / "Enemy" / "suicide-tank-down.png"
    SUICIDE_ENEMY_SPRITE_UP = ASSETS_DIR / "image" / "Enemy" / "suicide-tank-up.png"
    
    # ENEMY_SPRITE = ASSETS_DIR / "sprites" / "enemy.png"

    # ? Objetos
    BULLET_SPRITE = ASSETS_DIR / "image" / "Objects" / "Bombs" / "Bomb_A.png"
    ENEMY_BULLET_SPRITE = ASSETS_DIR / "image" / "Objects" / "Bombs" / "Bomb_B_01.png"  # Nueva bomba enemiga
    WALL_SPRITE = ASSETS_DIR / "image" / "Objects" / \
        "Bonus_Items" / "Attack_Bonus.png"
    EXPLOSION_SPRITE = ASSETS_DIR / "image" / \
        "Objects" / "Decor_Items" / "Blast_Trail_01.png"

    #* Fuentes
    # MAIN_FONT = ASSETS_DIR / "fonts" / "main_font.ttf"

    # * TILES
    BRICK_SPRITE = ASSETS_DIR / "image" / "Tileset" / "bricks.png"
    STEEL_SPRITE = ASSETS_DIR / "image" / "Tileset" / "wall-bottom.png"
    BASE_SPRITE = ASSETS_DIR / "image" / "Tileset" / "wall-bottom.png"
