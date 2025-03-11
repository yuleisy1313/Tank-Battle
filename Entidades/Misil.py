"""
    Yuleisy Carmona Vasquez
    22-SISN-2-016
"""

import pygame
from Utilidades.Constantes import Direction, CONSTANTES
from Utilidades.Assets import ASSETS


class Misil:
    def __init__(self, grid_x, grid_y, direction, tile_size=30):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * tile_size
        self.y = grid_y * tile_size
        self.direction = direction
        self.tile_size = tile_size

        # Atributos de movimiento
        self.speed = 4  # Más rápido que los tanques
        self.active = True

        # Bandera de misil enemigo (falso por defecto)
        self.is_enemy_missile = False

        # Cargar sprite de misil apropiado
        sprite_path = ASSETS.ENEMY_BULLET_SPRITE.value if self.is_enemy_missile else ASSETS.BULLET_SPRITE.value
        self.sprite = pygame.image.load(sprite_path).convert_alpha()
        self.sprite = pygame.transform.scale(
            self.sprite, (16, 16))  # Aumentado a 16x16
        self.image = self.sprite
        self.rect = self.image.get_rect()
        # Ajustado a -8 para centrar el sprite más grande
        self.rect.x = self.x + self.tile_size // 2 - 8
        # Ajustado a -8 para centrar el sprite más grande
        self.rect.y = self.y + self.tile_size // 2 - 8

    def update(self):
        # Solo actualizar si está activo
        if not self.active:
            return False

        # Mover en la dirección actual
        if self.direction == Direction.FRONT:
            self.y += self.speed
        elif self.direction == Direction.BACK:
            self.y -= self.speed
        elif self.direction == Direction.RIGHT:
            self.x += self.speed
        elif self.direction == Direction.LEFT:
            self.x -= self.speed

        # Actualizar posición en la cuadrícula
        self.grid_x = int(self.x // self.tile_size)
        self.grid_y = int(self.y // self.tile_size)

        # Actualizar rectángulo de colisión
        self.rect.x = self.x + self.tile_size // 2 - 2
        self.rect.y = self.y + self.tile_size // 2 - 4

        # Comprobar si está fuera de los límites
        if (self.x < 0 or self.x > CONSTANTES.WINDOW_SIZE.value[0] or
                self.y < 0 or self.y > CONSTANTES.WINDOW_SIZE.value[1]):
            return False

        return True

    def collide_with_map(self, game_map):
        # Obtener la posición actual en la cuadrícula
        grid_x = int(self.x // self.tile_size) 
        grid_y = int(self.y // self.tile_size)

        # Verificar si la posición es válida en el mapa
        if not game_map.es_posicion_valida(self.x, self.y):
            return True

        return False

    def draw(self, surface):
        # Rotar sprite basado en la dirección
        if self.direction == Direction.FRONT:
            rotated_sprite = pygame.transform.rotate(self.sprite, 180)  # Hacia abajo
        elif self.direction == Direction.BACK:
            rotated_sprite = pygame.transform.rotate(self.sprite, 0)    # Hacia arriba
        elif self.direction == Direction.RIGHT:
            rotated_sprite = pygame.transform.rotate(self.sprite, 270)  # Hacia la derecha
        elif self.direction == Direction.LEFT:
            rotated_sprite = pygame.transform.rotate(self.sprite, 90)   # Hacia la izquierda

        # Teñir de rojo para misiles enemigos
        if self.is_enemy_missile:
            rotated_sprite.fill(
                (255, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Dibujar el sprite en la superficie
        surface.blit(rotated_sprite, self.rect)
