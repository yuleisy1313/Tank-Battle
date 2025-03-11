"""
    Yuleisy Carmona Vasquez
    22-SISN-2-016
"""

import pygame
import math
from enum import Enum
from Algoritmos.Nodo import Accion, Secuencia, Selector, Timer
from Utilidades.Assets import ASSETS
from Utilidades.Constantes import Direction
from Utilidades.Setup import Setup


class JugadorState(Enum):
    IDLE = 1
    MOVING = 4
    PLANTING_BOMB = 4
    DAMAGED = 10


class Jugador:
    def __init__(self, grid_x, grid_y, game_map, tile_size=30):
        # Atributos básicos
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.map = game_map
        self.tile_size = tile_size

        # Posición y movimiento
        self.x = grid_x * tile_size
        self.y = grid_y * tile_size
        self.target_x = self.x
        self.target_y = self.y
        self.speed = 3.5
        self.is_moving = False

        # Dirección actual
        self.direction = Direction.FRONT

        # Estado y atributos del jugador
        self.state = JugadorState.IDLE
        self.health = 3  # El jugador comienza con 3 de salud

        # Invulnerabilidad después de ser golpeado
        self.invulnerable = False
        self.invulnerable_time = 0
        # 1.5 segundos de invulnerabilidad después de ser golpeado
        self.invulnerable_duration = 1500

        # Configuración de animaciones
        self.animation_frame = 0
        self.animation_speed = 3
        self.animation_timer = 0

        # Sonido
        self.sound_player = pygame.mixer.Sound(ASSETS.FIRE_SOUND.value)

        # Música de fondo para perder
        self.lose_music = pygame.mixer.Sound(ASSETS.LOSE_MUSIC.value)

        # Música de fondo para inicio del juego
        self.game_start_music = pygame.mixer.Sound(
            ASSETS.GAME_START_MUSIC.value)

        # Cargar sprites
        self.sprites = self.load_sprites()

        # Configurar imagen inicial
        self.image = self.sprites['front'][0]
        self.rect = self.image.get_rect()
        self.rect.x = self.x + 3  # Centrar el sprite
        self.rect.y = self.y + 3

        # Árbol de comportamiento
        self.setup_behavior_tree()

        # Tiempo del último misil disparado
        self.last_missile_time = 0

    def load_sprites(self):
        sprites = {
            'front': [],
            'back': [],
            'right': [],
            'left': []
        }

        # Cargar sprites direccionales
        front_image = pygame.image.load(
            str(ASSETS.TANK_SPRITE_DOWN.value)).convert_alpha()
        front_image = pygame.transform.scale(
            front_image, (self.tile_size - 2, self.tile_size - 2))
        sprites['front'].append(front_image)

        back_image = pygame.image.load(
            str(ASSETS.TANK_SPRITE_UP.value)).convert_alpha()
        back_image = pygame.transform.scale(
            back_image, (self.tile_size - 2, self.tile_size - 2))
        sprites['back'].append(back_image)

        right_image = pygame.image.load(
            str(ASSETS.TANK_SPRITE_RIGHT.value)).convert_alpha()
        right_image = pygame.transform.scale(
            right_image, (self.tile_size - 2, self.tile_size - 2))
        sprites['right'].append(right_image)

        left_image = pygame.image.load(
            str(ASSETS.TANK_SPRITE_LEFT.value)).convert_alpha()
        left_image = pygame.transform.scale(
            left_image, (self.tile_size - 2, self.tile_size - 2))
        sprites['left'].append(left_image)

        # Cargar sprites adicionales (actualmente vacíos, pero mantenemos la estructura)
        front_paths = []
        for path in front_paths:
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(
                image, (self.tile_size - 2, self.tile_size - 2))
            sprites['front'].append(image)

        # Cargar sprites traseros
        back_paths = []
        for path in back_paths:
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(
                image, (self.tile_size - 2, self.tile_size - 2))
            sprites['back'].append(image)

        # Cargar sprites derechos
        right_paths = []
        for path in right_paths:
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(
                image, (self.tile_size - 2, self.tile_size - 2))
            sprites['right'].append(image)

        # Cargar sprites izquierdos
        left_paths = []
        for path in left_paths:
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(
                image, (self.tile_size - 2, self.tile_size - 2))
            sprites['left'].append(image)

        return sprites

    def update_animation(self):
        self.animation_timer += self.animation_speed

        if self.animation_timer >= 1:
            self.animation_timer = 0
            if self.is_moving or self.state == JugadorState.MOVING:
                self.animation_frame = (
                    self.animation_frame + 1) % len(self.sprites[self.get_direction_key()])
            else:
                self.animation_frame = 0

        # Seleccionar sprite según dirección y estado
        direction_key = self.get_direction_key()
        # Verificar que hay sprites disponibles
        if len(self.sprites[direction_key]) > 0:
            self.image = self.sprites[direction_key][min(
                self.animation_frame, len(self.sprites[direction_key])-1)]

    def get_direction_key(self):
        """Método auxiliar para obtener la clave de dirección actual"""
        direction_map = {
            Direction.FRONT: 'front',
            Direction.BACK: 'back',
            Direction.RIGHT: 'right',
            Direction.LEFT: 'left'
        }
        return direction_map[self.direction]

    def update_rect_position(self):
        """Actualiza la posición del rectángulo del sprite"""
        self.rect.x = self.x + 3  # Ajuste para centrar
        self.rect.y = self.y + 3

    def setup_behavior_tree(self):
        """
        Configura el árbol de comportamiento del jugador

        El jugador tiene dos acciones básicas:
        - Moverse
        - Actualizar la animación

        El jugador también tiene un timer para controlar la animación

        Para agregar mas comportamientos, ejemplo como disparar, se puede agregar mas acciones
        y agregarlas al selector principal
        """
        # Acciones básicas
        mover = Accion(self.move)
        actualizar_animacion = Accion(self.update_animation)

        # Crear la secuencia y agregar los hijos individualmente
        secuencia_movimiento = Secuencia()
        secuencia_movimiento.agregar_hijo(mover)
        secuencia_movimiento.agregar_hijo(actualizar_animacion)

        # Timer para control de animación
        timer_animacion = Timer(0.1)

        # Selector principal
        self.comportamiento = Selector()
        self.comportamiento.agregar_hijo(secuencia_movimiento)
        self.comportamiento.agregar_hijo(timer_animacion)

    def draw(self, screen):
        # Hacer parpadear al jugador cuando está invulnerable
        if self.invulnerable:
            if pygame.time.get_ticks() % 200 < 100:  # Parpadea cada 100ms
                screen.blit(self.image, self.rect)
        else:
            screen.blit(self.image, self.rect)

        # Mostrar barra de salud encima del jugador
        self.draw_health_bar(screen)

    def update(self):
        # Actualizar estado de invulnerabilidad
        current_time = pygame.time.get_ticks()
        if self.invulnerable and current_time - self.invulnerable_time > self.invulnerable_duration:
            self.invulnerable = False

        # Procesar entrada de joystick si está disponible, pero sin interferir con el teclado
        if Setup.is_joystick_connected() and Setup.process_joystick_cooldown(current_time):
            joystick = Setup.joystick

            # Verificar botones del joystick para disparar (independiente del movimiento)
            if joystick.get_button(0) or joystick.get_button(2):  # Botones A o X
                self.fire_missile()
                Setup.set_joystick_cooldown(current_time)

            # Solo procesar movimiento con joystick si no estamos ya en movimiento desde el teclado
            if not self.is_moving:
                # Manejar movimiento con joystick
                axis_x = joystick.get_axis(0)
                axis_y = joystick.get_axis(1)
                if abs(axis_x) > 0.1 or abs(axis_y) > 0.1:
                    self.move_with_joystick(axis_x, axis_y)
                    Setup.set_joystick_cooldown(current_time)

                # Manejar movimiento con D-pad si está disponible
                elif joystick.get_numhats() > 0:
                    hat_x, hat_y = joystick.get_hat(0)
                    if hat_x != 0 or hat_y != 0:
                        # Convertir D-pad a valores de eje (-1, 0, 1)
                        # Invertir y para coincidencia con ejes
                        self.move_with_joystick(hat_x, -hat_y)
                        Setup.set_joystick_cooldown(current_time)

        # El árbol de comportamiento incluye move() que maneja el teclado
        self.comportamiento.ejecutar()
        self.update_animation()

    def get_position_for_astar(self):
        """Retorna la posición actual del jugador en coordenadas de la cuadrícula para el pathfinding"""
        return (self.grid_x, self.grid_y)

    def move(self):
        """Mueve al jugador en la dirección especificada"""
        if self.is_moving:
            # Si ya está en movimiento, continuar con el movimiento actual
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance < self.speed:
                self.x = self.target_x
                self.y = self.target_y
                self.is_moving = False
                self.grid_x = self.x // self.tile_size
                self.grid_y = self.y // self.tile_size
                self.state = JugadorState.IDLE
            else:
                move_x = (dx / distance) * self.speed
                move_y = (dy / distance) * self.speed
                self.x += move_x
                self.y += move_y
        else:
            # Obtener entrada desde Setup (teclado o joystick)
            dx, dy = Setup.get_movement_input()

            # Solo procesamos si hay movimiento significativo
            if abs(dx) > 0.1 or abs(dy) > 0.1:
                # Determinar la dirección principal basada en qué eje tiene mayor valor absoluto
                if abs(dx) > abs(dy):
                    # Movimiento horizontal
                    new_grid_x = self.grid_x + (1 if dx > 0 else -1)
                    new_grid_y = self.grid_y
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    # Movimiento vertical
                    new_grid_x = self.grid_x
                    new_grid_y = self.grid_y + (1 if dy > 0 else -1)
                    self.direction = Direction.FRONT if dy > 0 else Direction.BACK

                # Verificar si la nueva posición es válida
                if (0 <= new_grid_x < self.map.ancho and
                    0 <= new_grid_y < self.map.alto and
                    self.map.es_posicion_valida(new_grid_x * self.tile_size, new_grid_y * self.tile_size) and
                        not self.is_tank_at_position(new_grid_x, new_grid_y)):

                    self.target_x = new_grid_x * self.tile_size
                    self.target_y = new_grid_y * self.tile_size
                    self.is_moving = True
                    self.state = JugadorState.MOVING

            # Verificar disparo con función centralizada
            if Setup.is_fire_pressed():
                self.fire_missile()

        self.update_rect_position()

    def is_tank_at_position(self, grid_x, grid_y):
        """Esto será implementado por la clase Game e inyectado al Jugador"""
        # Implementación por defecto retorna False
        # Esto será sobrescrito por Game
        return False

    def move_with_joystick(self, axis_x, axis_y):
        """
        Mueve al jugador en la dirección especificada por el joystick
        """
        if not self.is_moving:
            # Determinar la dirección principal basada en qué eje tiene mayor valor absoluto
            if abs(axis_x) > abs(axis_y):
                # Movimiento horizontal
                if axis_x < -0.1:
                    new_grid_x = self.grid_x - 1
                    new_grid_y = self.grid_y
                    self.direction = Direction.LEFT
                elif axis_x > 0.1:
                    new_grid_x = self.grid_x + 1
                    new_grid_y = self.grid_y
                    self.direction = Direction.RIGHT
                else:
                    return  # No hay suficiente entrada para moverse
            else:
                # Movimiento vertical
                if axis_y < -0.1:
                    new_grid_x = self.grid_x
                    new_grid_y = self.grid_y - 1
                    self.direction = Direction.BACK
                elif axis_y > 0.1:
                    new_grid_x = self.grid_x
                    new_grid_y = self.grid_y + 1
                    self.direction = Direction.FRONT
                else:
                    return  # No hay suficiente entrada para moverse

            # Verificar si puede moverse a la nueva posición
            if (0 <= new_grid_x < self.map.ancho and
                0 <= new_grid_y < self.map.alto and
                self.map.es_posicion_valida(new_grid_x * self.tile_size, new_grid_y * self.tile_size) and
                    not self.is_tank_at_position(new_grid_x, new_grid_y)):

                self.target_x = new_grid_x * self.tile_size
                self.target_y = new_grid_y * self.tile_size
                self.is_moving = True
                self.state = JugadorState.MOVING

            self.update_rect_position()

    def take_damage(self, amount):
        """Maneja el daño recibido por el jugador"""
        # Si ya está invulnerable, ignorar el daño
        if self.invulnerable:
            return

        # Aplicar daño
        self.health -= amount

        # Activar invulnerabilidad
        self.invulnerable = True
        self.invulnerable_time = pygame.time.get_ticks()

        # Establecer temporalmente el estado de dañado
        self.state = JugadorState.DAMAGED

        # Reproducir sonido de daño
        pygame.mixer.Sound.play(pygame.mixer.Sound(
            str(ASSETS.FIRE_SOUND.value)))

        # Comprobar si el jugador ha perdido toda su salud
        if self.health <= 0:
            self.play_lose_music()

    def play_lose_music(self):
        """Reproducir música de fondo cuando el jugador pierde"""
        pygame.mixer.Sound.play(self.lose_music)

    def play_game_start_music(self):
        """Reproducir música de fondo cuando inicia el juego"""
        pygame.mixer.Sound.play(self.game_start_music)

    def draw_health_bar(self, screen):
        """Dibujar una barra de salud encima del jugador"""
        bar_width = self.tile_size - 6
        bar_height = 4
        bar_x = self.x + 3
        bar_y = self.y - 8

        # Fondo (rojo)
        pygame.draw.rect(screen, (255, 0, 0),
                         pygame.Rect(bar_x, bar_y, bar_width, bar_height))

        # Salud (verde)
        health_width = max(0, (self.health / 3) * bar_width)
        pygame.draw.rect(screen, (0, 255, 0),
                         pygame.Rect(bar_x, bar_y, health_width, bar_height))

    def fire_missile(self):
        """Disparar un misil en la dirección a la que apunta el jugador"""
        # Obtener el tiempo actual
        current_time = pygame.time.get_ticks()

        # Comprobar si ha pasado el tiempo de enfriamiento
        if current_time - self.last_missile_time < 500:  # 500ms de enfriamiento
            return None

        # Actualizar el tiempo del último misil
        self.last_missile_time = current_time

        # Calcular la posición del misil basada en la dirección del jugador
        if self.direction == Direction.FRONT:
            missile_x = self.grid_x
            missile_y = self.grid_y + 1
        elif self.direction == Direction.BACK:
            missile_x = self.grid_x
            missile_y = self.grid_y - 1
        elif self.direction == Direction.RIGHT:
            missile_x = self.grid_x + 1
            missile_y = self.grid_y
        else:  # LEFT
            missile_x = self.grid_x - 1
            missile_y = self.grid_y

        # Reproducir sonido
        pygame.mixer.Sound.play(self.sound_player)

        # La clase Game manejará la creación real del misil
        # Solo devolver la posición y dirección por ahora
        return {
            "position": (missile_x, missile_y),
            "direction": self.direction
        }
