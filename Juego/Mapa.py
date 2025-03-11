"""
    Yuleisy Carmona Vasquez
    22-SISN-2-016
"""

import pygame as pg
from Utilidades.Constantes import CONSTANTES
from Utilidades.Assets import ASSETS
from enum import Enum
import random


class TileType(Enum):
    """ Tipos de celdas en el mapa """
    EMPTY = 0
    BRICK = 1
    STEEL = 2
    BASE = 3


class Mapa:
    def __init__(self, ancho=13, alto=13):
        self.ancho = ancho
        self.alto = alto
        self.tile_size = CONSTANTES.TILE_SIZE.value
        self.grid = [
            [TileType.EMPTY for _ in range(ancho)] for _ in range(alto)]
        self.sprites = {
            TileType.BRICK: pg.image.load(str(ASSETS.BRICK_SPRITE.value)),
            TileType.STEEL: pg.image.load(str(ASSETS.STEEL_SPRITE.value)),
            TileType.BASE: pg.image.load(str(ASSETS.BASE_SPRITE.value)),
        }

        # Escalar los sprites al tamaño de la celda
        for tile_type, sprite in self.sprites.items():
            self.sprites[tile_type] = pg.transform.scale(
                sprite, (self.tile_size, self.tile_size))

        self.background = pg.image.load(str(ASSETS.GAME_BACKGROUND.value))
        self.background = pg.transform.scale(
            self.background, CONSTANTES.WINDOW_SIZE.value)

        # Puntos de aparición de enemigos
        self.enemy_spawn_points = []

        # Generar mapa inicial
        self.generar_mapa()

    def generar_mapa(self):
        # Generar un mapa aleatorio simple
        # Añadir bordes
        for x in range(self.ancho):
            self.grid[0][x] = TileType.STEEL
            self.grid[self.alto-1][x] = TileType.STEEL

        for y in range(self.alto):
            self.grid[y][0] = TileType.STEEL
            self.grid[y][self.ancho-1] = TileType.STEEL

        # Añadir muros de ladrillo aleatorios
        for _ in range(30):
            x = random.randint(2, self.ancho - 3)
            y = random.randint(2, self.alto - 3)
            self.grid[y][x] = TileType.BRICK

        # Añadir algunos muros de acero
        for _ in range(10):
            x = random.randint(2, self.ancho - 3)
            y = random.randint(2, self.alto - 3)
            self.grid[y][x] = TileType.STEEL

        # Crear puntos de aparición para enemigos en las esquinas y lados del mapa
        self.enemy_spawn_points = [
            (1, 1),                      # Esquina superior izquierda
            (self.ancho - 2, 1),         # Esquina superior derecha
            (1, self.alto - 2)           # Esquina inferior izquierda
        ]

        # Asegurarse de que los puntos de aparición estén vacíos
        for x, y in self.enemy_spawn_points:
            self.grid[y][x] = TileType.EMPTY

    def get_enemy_spawn_points(self):
        """Devuelve los puntos de aparición para enemigos en las esquinas"""
        return self.enemy_spawn_points

    def dibujar(self, superficie):
        # Dibujar fondo
        superficie.blit(self.background, (0, 0))

        # Dibujar elementos del mapa
        for y in range(self.alto):
            for x in range(self.ancho):
                tile_type = self.grid[y][x]
                if tile_type != TileType.EMPTY:
                    superficie.blit(
                        self.sprites[tile_type], (x * self.tile_size, y * self.tile_size))

    def es_posicion_valida(self, x, y):
        # Verificar si una posición es válida para moverse
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)

        if not (0 <= tile_x < self.ancho and 0 <= tile_y < self.alto):
            return False

        return self.grid[tile_y][tile_x] == TileType.EMPTY

    def destruir_bloque(self, x, y):
        # Destruir un bloque en las coordenadas dadas
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)

        if 0 <= tile_x < self.ancho and 0 <= tile_y < self.alto:
            if self.grid[tile_y][tile_x] == TileType.BRICK:
                self.grid[tile_y][tile_x] = TileType.EMPTY
                return True

        return False
