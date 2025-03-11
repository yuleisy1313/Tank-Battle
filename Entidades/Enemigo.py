"""
    Yuleisy Carmona Vasquez
    22-SISN-2-016
"""

import pygame
import math
import random
from enum import Enum
from Algoritmos.Nodo import Accion, Secuencia, Selector, Timer
from Utilidades.Assets import ASSETS
from Utilidades.Constantes import Direction
from Algoritmos.A_Star import AStar


class EnemigoState(Enum):
    IDLE = 1
    PATROLLING = 2
    PURSUING = 3
    ATTACKING = 4
    DAMAGED = 5


class Enemigo:
    def __init__(self, grid_x, grid_y, game_map, player=None, tile_size=30):
        # Atributos básicos
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.map = game_map
        self.player = player
        self.tile_size = tile_size

        # Posición y movimiento
        self.x = grid_x * tile_size
        self.y = grid_y * tile_size
        self.target_x = self.x
        self.target_y = self.y
        self.speed = 0.8
        self.is_moving = False

        # Dirección actual
        self.direction = Direction.FRONT

        # Estado y atributos del enemigo
        self.state = EnemigoState.PATROLLING
        self.max_health = 50
        self.health = self.max_health

        # Atributos de ataque
        self.attack_range = 8
        self.last_patrol_change = pygame.time.get_ticks()
        self.patrol_change_interval = 3000  # Cambiar dirección cada 3 segundos

        # Punto de inicio para patrullar
        self.spawn_x = grid_x
        self.spawn_y = grid_y
        self.patrol_radius = 6
        self.long_patrol_chance = 0.4

        # Configuración de animaciones
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0

        # Pathfinding
        self.pathfinder = AStar(game_map)
        self.current_path = []
        self.path_index = 0
        self.path_update_timer = pygame.time.get_ticks()
        self.path_update_interval = 1000  # Actualizar camino cada segundo

        # Sonido
        self.sound_enemy = pygame.mixer.Sound(ASSETS.FIRE_SOUND.value)

        # Cargar sprites
        self.sprites = self.load_sprites()

        # Configurar imagen inicial
        self.image = self.sprites['front'][0]
        self.rect = self.image.get_rect()
        self.rect.x = self.x + 3
        self.rect.y = self.y + 3

        # Árbol de comportamiento
        self.setup_behavior_tree()

        # Disparo
        self.can_shoot = True
        self.last_shot_time = pygame.time.get_ticks()

        # Random enfriamiento de disparo
        self.shoot_cooldown = random.randint(1500, 1800)
        self.shoot_range = 5

        self.juego = None  # Referencia al juego

    def load_sprites(self):
        sprites = {
            'front': [],
            'back': [],
            'right': [],
            'left': []
        }

        # Cargamos los sprites enemigos - usaremos temporalmente los mismos que el jugador pero con un tinte rojo
        front_image = pygame.image.load(
            str(ASSETS.TANK_SPRITE_DOWN.value)).convert_alpha()
        front_image = pygame.transform.scale(
            front_image, (self.tile_size - 2, self.tile_size - 2))
        # Dar tinte rojo al enemigo
        red_tint = pygame.Surface(front_image.get_size()).convert_alpha()
        red_tint.fill((255, 0, 0, 100))
        front_image.blit(red_tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        sprites['front'].append(front_image)

        back_image = pygame.image.load(
            str(ASSETS.TANK_SPRITE_UP.value)).convert_alpha()
        back_image = pygame.transform.scale(
            back_image, (self.tile_size - 2, self.tile_size - 2))
        back_image.blit(red_tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        sprites['back'].append(back_image)

        right_image = pygame.image.load(
            str(ASSETS.TANK_SPRITE_RIGHT.value)).convert_alpha()
        right_image = pygame.transform.scale(
            right_image, (self.tile_size - 2, self.tile_size - 2))
        right_image.blit(red_tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        sprites['right'].append(right_image)

        left_image = pygame.image.load(
            str(ASSETS.TANK_SPRITE_LEFT.value)).convert_alpha()
        left_image = pygame.transform.scale(
            left_image, (self.tile_size - 2, self.tile_size - 2))
        left_image.blit(red_tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        sprites['left'].append(left_image)

        return sprites

    def update_animation(self):
        self.animation_timer += self.animation_speed

        if self.animation_timer >= 1:
            self.animation_timer = 0
            if self.is_moving or self.state in [EnemigoState.PATROLLING, EnemigoState.PURSUING]:
                self.animation_frame = (
                    self.animation_frame + 1) % len(self.sprites[self.get_direction_key()])
            else:
                self.animation_frame = 0

        # Seleccionar sprite según dirección y estado
        direction_key = self.get_direction_key()
        if len(self.sprites[direction_key]) > 0:
            self.image = self.sprites[direction_key][min(
                self.animation_frame, len(self.sprites[direction_key])-1)]

        # Retorno explícito para el árbol de comportamiento
        return True

    def get_direction_key(self):
        """Método auxiliar para obtener la clave de la dirección actual"""
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
        """Configura el árbol de comportamiento del enemigo"""
        # Acciones básicas
        check_player_visible = Accion(self.is_player_visible)
        pursue_player = Accion(self.pursue_player)
        patrol = Accion(self.patrol)
        update_animation = Accion(self.update_animation)
        update_position = Accion(self.update_position)
        try_shoot = Accion(self.try_shoot)

        # CORRECTED: Construir una estructura de árbol de comportamiento más robusta

        # Secuencia de movimiento: selecciona comportamiento y actualiza posición
        secuencia_movimiento = Secuencia()

        # Selector de comportamiento (perseguir o patrullar)
        selector_comportamiento = Selector()

        # Secuencia para perseguir
        secuencia_perseguir = Secuencia()
        secuencia_perseguir.agregar_hijo(check_player_visible)
        secuencia_perseguir.agregar_hijo(pursue_player)

        # Añadir comportamientos al selector
        selector_comportamiento.agregar_hijo(
            secuencia_perseguir)  # Primero intentar perseguir
        selector_comportamiento.agregar_hijo(
            patrol)              # Si no, patrullar

        # Añadir selector de comportamiento a la secuencia de movimiento
        secuencia_movimiento.agregar_hijo(selector_comportamiento)
        secuencia_movimiento.agregar_hijo(update_position)

        # Secuencia de disparo
        secuencia_disparar = Secuencia()
        secuencia_disparar.agregar_hijo(check_player_visible)
        secuencia_disparar.agregar_hijo(try_shoot)

        # Secuencia principal
        secuencia_principal = Secuencia()
        secuencia_principal.agregar_hijo(
            secuencia_movimiento)   # Manejar movimiento
        secuencia_principal.agregar_hijo(Selector(
            # Intentar disparar o continuar
            [secuencia_disparar, Accion(lambda: True)]))
        secuencia_principal.agregar_hijo(
            update_animation)       # Actualizar animación

        self.comportamiento = secuencia_principal

    def draw(self, screen):
        # Dibujar el tanque enemigo
        screen.blit(self.image, self.rect)

        # Dibujar barra de salud
        self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
        """Dibujar una barra de salud sobre el tanque enemigo"""
        bar_width = self.tile_size - 6
        bar_height = 4
        bar_x = self.x + 3
        bar_y = self.y - 8

        # Fondo (rojo)
        pygame.draw.rect(screen, (255, 0, 0),
                         pygame.Rect(bar_x, bar_y, bar_width, bar_height))

        # Salud (verde)
        health_width = max(0, (self.health / self.max_health) * bar_width)
        pygame.draw.rect(screen, (0, 255, 0),
                         pygame.Rect(bar_x, bar_y, health_width, bar_height))

    def take_damage(self, amount):
        """Manejar el daño recibido por el enemigo"""
        self.health -= amount
        self.state = EnemigoState.DAMAGED

        # Retorna True si el enemigo debe ser destruido
        if self.health <= 0:
            if self.juego:
                self.juego.enemigos_destruidos += 1
            return True
        return False

    def update(self):
        """Actualizar el estado y comportamiento del enemigo"""
        # Ejecutar el árbol de comportamiento
        result = self.comportamiento.ejecutar()

        # Si el árbol de comportamiento falló por completo, intenta una patrulla simple como respaldo
        if not result and not self.is_moving:
            self.try_random_movement()

        return result

    def calculate_path_to_player(self):
        """Calcular camino al jugador usando el algoritmo A*, considerando todas las posiciones de los tanques"""
        if not self.player:
            return False

        # Obtener todas las posiciones ocupadas del juego
        all_occupied_positions = self.get_all_occupied_positions()

        # Obtener posiciones en la cuadrícula
        start = (self.grid_x, self.grid_y)
        goal = (self.player.grid_x, self.player.grid_y)

        # Usar A* para encontrar el camino, pasando posiciones ocupadas
        path = self.pathfinder.find_path(start, goal, all_occupied_positions)
        if path and len(path) > 0:
            self.current_path = path
            self.path_index = 0
            return True
        return False

    def get_all_occupied_positions(self):
        """Obtener posiciones de todos los tanques en el juego"""
        occupied = []

        # Esta función debe ser inyectada desde la clase del juego
        # Pero por ahora, implementaremos un respaldo
        if hasattr(self, 'get_all_tank_positions'):
            return self.get_all_tank_positions()

        # Agregar posición del jugador si está disponible
        if self.player:
            occupied.append((self.player.grid_x, self.player.grid_y))

        return occupied

    def is_player_visible(self):
        """Verificar si el jugador es visible con una verificación mejorada de línea de visión"""
        if not self.player:
            return False

        # Calcular distancia al jugador
        dx = abs(self.grid_x - self.player.grid_x)
        dy = abs(self.grid_y - self.player.grid_y)
        distance = math.sqrt(dx**2 + dy**2)

        # Si el jugador está dentro del rango, verificar línea de visión
        if distance <= self.attack_range:
            # Primero, realizar una verificación de visibilidad directa sin importar la dirección
            if self.has_line_of_sight():
                # Si el jugador es visible, enfrentar al jugador y establecer estado a persiguiendo
                self.face_player()
                self.state = EnemigoState.PURSUING
                return True

            # Si no es directamente visible, verificar si el jugador está en el campo de visión basado en la dirección
            elif self.player_in_front() and self.has_line_of_sight():
                self.state = EnemigoState.PURSUING
                return True

        # Si estaba persiguiendo pero ahora perdió de vista, regresa a patrullar
        if self.state == EnemigoState.PURSUING:
            self.state = EnemigoState.PATROLLING
            self.current_path = []  # Limpiar el camino al regresar a patrullar

        return False

    def player_in_front(self):
        """Verificar si el jugador está al frente basado en la dirección del enemigo"""
        if not self.player:
            return False

        dx = self.player.grid_x - self.grid_x
        dy = self.player.grid_y - self.grid_y

        # Verificar basado en la dirección
        if ((self.direction == Direction.FRONT or
             self.direction == Direction.BACK or
             self.direction == Direction.RIGHT or
             self.direction == Direction.LEFT) and
                dy > 0 and abs(dy) > abs(dx)):
            return True

        return False

    def has_line_of_sight(self):
        """Verificar si hay una línea de visión clara hacia el jugador"""
        if not self.player:
            return False

        # Obtener posiciones
        start_x, start_y = self.grid_x, self.grid_y
        end_x, end_y = self.player.grid_x, self.player.grid_y

        # Usar el algoritmo de línea de Bresenham para revisar los espacios entre el enemigo y el jugador
        points = self.bresenham_line(start_x, start_y, end_x, end_y)

        # Verificar cada punto en la línea
        # Omitir el primer punto (posición del enemigo)
        for x, y in points[1:]:
            if not self.map.es_posicion_valida(x * self.tile_size, y * self.tile_size):
                return False

        return True

    def bresenham_line(self, x0, y0, x1, y1):
        """Implementación del algoritmo de línea de Bresenham"""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return points

    def try_shoot(self):
        """Intentar disparar al jugador si está en rango y el enfriamiento está listo"""
        if not self.player:
            return False

        # Calcular distancia al jugador
        dx = abs(self.grid_x - self.player.grid_x)
        dy = abs(self.grid_y - self.player.grid_y)
        distance = math.sqrt(dx**2 + dy**2)

        current_time = pygame.time.get_ticks()

        # Verificar si podemos disparar (el enfriamiento ha pasado y el jugador está dentro del rango de disparo)
        if distance <= self.shoot_range and current_time - self.last_shot_time > self.shoot_cooldown:
            # Actualizar enfriamiento
            self.last_shot_time = current_time

            # Actualizar dirección para enfrentar al jugador antes de disparar
            self.face_player()

            # Crear realmente el misil en la clase Juego
            # Retornamos True para indicar que se debe realizar un disparo
            self.state = EnemigoState.ATTACKING
            return True

        return False

    def face_player(self):
        """Actualiza la dirección para enfrentar al jugador"""
        if not self.player:
            return

        dx = self.player.grid_x - self.grid_x
        dy = self.player.grid_y - self.grid_y

        # Determinar la dirección principal (mayor desplazamiento)
        if abs(dx) > abs(dy):
            # El movimiento horizontal es principal
            if dx > 0:
                self.direction = Direction.RIGHT
            else:
                self.direction = Direction.LEFT
        else:
            # El movimiento vertical es principal
            if dy > 0:
                self.direction = Direction.FRONT
            else:
                self.direction = Direction.BACK

    def get_missile_position(self):
        """Retornar la posición para un nuevo misil basado en la dirección del tanque"""
        # Posicionar delante del tanque basado en la dirección
        if self.direction == Direction.FRONT:
            return self.grid_x, self.grid_y + 1
        elif self.direction == Direction.BACK:
            return self.grid_x, self.grid_y - 1
        elif self.direction == Direction.RIGHT:
            return self.grid_x + 1, self.grid_y
        else:  # LEFT
            return self.grid_x - 1, self.grid_y

    def pursue_player(self):
        """Persigue al jugador siguiendo el camino calculado"""
        current_time = pygame.time.get_ticks()

        # Si está en movimiento, continuar con el movimiento actual
        if self.is_moving:
            return True

        # Recalcular el camino periódicamente o si no hay camino
        if not self.current_path or self.path_index >= len(self.current_path) or \
           current_time - self.path_update_timer > self.path_update_interval:
            self.path_update_timer = current_time

            if not self.calculate_path_to_player():
                # Si no se puede calcular un camino, intentar con patrulla
                self.state = EnemigoState.PATROLLING
                return False

            self.path_index = 0

        # Si hay un camino válido, seguirlo
        if self.path_index < len(self.current_path):
            next_pos = self.current_path[self.path_index]

            # Si ya estamos en la posición, pasar a la siguiente
            if (self.grid_x, self.grid_y) == next_pos:
                self.path_index += 1

                if self.path_index >= len(self.current_path):
                    # Llegamos al final del camino
                    self.state = EnemigoState.PURSUING
                    return True

                next_pos = self.current_path[self.path_index]

            # Verificar si la siguiente posición es válida y no está ocupada
            if (self.map.es_posicion_valida(next_pos[0] * self.tile_size, next_pos[1] * self.tile_size) and
                    not self.position_occupied_by_tank(next_pos[0], next_pos[1])):

                # Mover al siguiente punto
                self.target_x = next_pos[0] * self.tile_size
                self.target_y = next_pos[1] * self.tile_size
                self.is_moving = True

                # Actualizar dirección
                self.update_direction_from_movement(
                    next_pos[0] - self.grid_x,
                    next_pos[1] - self.grid_y
                )

                self.state = EnemigoState.PURSUING
                return True
            else:
                # Si la posición está bloqueada, recalcular camino
                self.current_path = []
                self.state = EnemigoState.IDLE
                return False

        # Si no hay más puntos en el camino
        self.state = EnemigoState.PATROLLING
        return False

    def _get_long_patrol_points(self):
        """Buscar puntos potenciales para una patrulla de larga distancia"""
        possible_points = []
        for _ in range(15):  # Intentar hasta 15 posiciones aleatorias
            new_x = random.randint(1, self.map.ancho - 2)
            new_y = random.randint(1, self.map.alto - 2)

            # Verificar si la posición es válida y no está ocupada
            if (self.map.es_posicion_valida(new_x * self.tile_size, new_y * self.tile_size) and
                    not self.position_occupied_by_tank(new_x, new_y)):

                # Asegurarse de que sea significativamente diferente de la posición actual
                distance = math.sqrt(
                    (new_x - self.grid_x)**2 + (new_y - self.grid_y)**2)
                if distance > 3:  # Al menos 3 casillas de distancia
                    possible_points.append((new_x, new_y))
        return possible_points

    def _get_nearby_patrol_points(self):
        """Encontrar puntos de patrulla potenciales cerca de la posición actual"""
        possible_points = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        # Aleatorizar para un movimiento más natural
        random.shuffle(directions)

        for dx, dy in directions:
            new_x = self.grid_x + dx
            new_y = self.grid_y + dy

            if self._is_valid_position(new_x, new_y):
                possible_points.append((new_x, new_y))
        return possible_points

    def _get_wider_area_patrol_points(self):
        """Buscar en un área más amplia para puntos de patrulla"""
        possible_points = []
        radius = 3  # Radio de búsqueda
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:  # Omitir la posición actual
                    continue

                new_x = self.grid_x + dx
                new_y = self.grid_y + dy

                if self._is_valid_position(new_x, new_y):
                    possible_points.append((new_x, new_y))
        return possible_points

    def _is_valid_position(self, x, y):
        """Verificar si la posición es válida y no está ocupada"""
        return (0 <= x < self.map.ancho and
                0 <= y < self.map.alto and
                self.map.es_posicion_valida(x * self.tile_size, y * self.tile_size) and
                not self.position_occupied_by_tank(x, y))

    def _move_to_patrol_point(self, target_x, target_y):
        """Establecer movimiento hacia un punto de patrulla"""
        self.target_x = target_x * self.tile_size
        self.target_y = target_y * self.tile_size
        self.is_moving = True
        self.update_direction_from_movement(
            target_x - self.grid_x, target_y - self.grid_y)
        self.state = EnemigoState.PATROLLING
        return True

    def patrol(self):
        """Comportamiento de patrulla por todo el mapa"""
        # Si está en movimiento, continuar con el movimiento actual
        if self.is_moving:
            return True

        current_time = pygame.time.get_ticks()
        # Si no está en movimiento, verificar si debe cambiar de dirección
        if current_time - self.last_patrol_change > self.patrol_change_interval:
            self.last_patrol_change = current_time

            # Buscar puntos de patrulla
            possible_points = []
            if random.random() < self.long_patrol_chance:
                possible_points = self._get_long_patrol_points()
            else:
                possible_points = self._get_nearby_patrol_points()

            # Si no se encuentran puntos, intentar una búsqueda más amplia
            if not possible_points:
                possible_points = self._get_wider_area_patrol_points()

            # Moverse a un punto seleccionado si se encuentra
            if possible_points:
                target_x, target_y = random.choice(possible_points)
                return self._move_to_patrol_point(target_x, target_y)

        # Si no se ha encontrado un punto para patrullar
        if not self.is_moving:
            self.state = EnemigoState.PATROLLING
            self.try_random_movement()

        return False

    def try_random_movement(self):
        """Intentar moverse en una dirección aleatoria si no hay un camino de patrulla disponible"""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            new_x = self.grid_x + dx
            new_y = self.grid_y

            if (0 <= new_x < self.map.ancho and
                0 <= new_y < self.map.alto and
                self.map.es_posicion_valida(new_x * self.tile_size, new_y * self.tile_size) and
                    not self.position_occupied_by_tank(new_x, new_y)):

                self.target_x = new_x * self.tile_size
                self.target_y = new_y * self.tile_size
                self.is_moving = True

                # Actualizar dirección
                self.update_direction_from_movement(dx, dy)
                break

    def position_occupied_by_tank(self, grid_x, grid_y):
        """Verificar si la posición está ocupada por otro tanque"""
        # Este método debe ser sobrescrito por la clase Juego
        # No llamar a self.__class__.position_occupied_by_tank ya que crea recursión infinita

        # Si tenemos una función inyectada de la clase Juego, úsala
        if hasattr(self, 'get_all_tank_positions') and callable(getattr(self, 'get_all_tank_positions')):
            all_positions = self.get_all_tank_positions()
            return (grid_x, grid_y) in all_positions

        return False

    def update_position(self):
        """Actualiza la posición del enemigo cuando está en movimiento"""
        if not self.is_moving:
            self.update_rect_position()
            return True

        # Obtener las coordenadas de cuadrícula de la posición objetivo
        target_grid_x = self.target_x // self.tile_size
        target_grid_y = self.target_y // self.tile_size

        # Verificar obstáculos en el camino
        if not self._is_path_clear(target_grid_x, target_grid_y):
            return False

        # Verificar colisión con otros tanques
        if not self._is_target_position_free(target_grid_x, target_grid_y):
            return False

        # Calcular distancia y moverse
        return self._move_towards_target()

    def _is_path_clear(self, target_grid_x, target_grid_y):
        """Verifica si el camino hacia el objetivo está libre de obstáculos"""
        for y in range(min(self.grid_y, target_grid_y), max(self.grid_y, target_grid_y) + 1):
            for x in range(min(self.grid_x, target_grid_x), max(self.grid_x, target_grid_x) + 1):
                if not self.map.es_posicion_valida(x * self.tile_size, y * self.tile_size):
                    # Camino bloqueado
                    self.is_moving = False
                    self.current_path = []
                    return False
        return True

    def _is_target_position_free(self, target_grid_x, target_grid_y):
        """Verifica si la posición objetivo está libre de otros tanques"""
        # Si el objetivo es la posición actual, está libre
        if (target_grid_x, target_grid_y) == (self.grid_x, self.grid_y):
            return True

        # Verificar con las posiciones de todos los tanques si está disponible
        if hasattr(self, 'get_all_tank_positions'):
            all_positions = self.get_all_tank_positions()
            current_pos = (self.grid_x, self.grid_y)
            all_positions_except_self = [
                pos for pos in all_positions if pos != current_pos]

            if (target_grid_x, target_grid_y) in all_positions_except_self:
                self.is_moving = False
                self.current_path = []
                return False
        return True

    def _move_towards_target(self):
        """Moverse hacia la posición objetivo"""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Si estamos muy cerca del objetivo, consideramos que hemos llegado
        if distance < self.speed:
            return self._reach_target_position()
        else:
            return self._move_incrementally(dx, dy, distance)

    def _reach_target_position(self):
        """Manejar cuando se alcanza la posición objetivo"""
        # Establecer posición exactamente en el objetivo
        self.x = self.target_x
        self.y = self.target_y
        self.is_moving = False
        self.grid_x = int(self.x // self.tile_size)
        self.grid_y = int(self.y // self.tile_size)

        # Si hay un camino y no hemos llegado al final, avanzar al siguiente punto
        if self.current_path and self.path_index < len(self.current_path) - 1:
            self.path_index += 1

        # Actualizar la posición del rectángulo de colisión
        self.update_rect_position()
        return True

    def _move_incrementally(self, dx, dy, distance):
        """Mover incrementalmente hacia el objetivo con detección de colisiones"""
        move_x = (dx / distance) * self.speed
        move_y = (dy / distance) * self.speed

        next_x = self.x + move_x
        next_y = self.y + move_y
        next_grid_x = int(next_x // self.tile_size)
        next_grid_y = int(next_y // self.tile_size)

        # Verificar colisiones y ajustar el movimiento si es necesario
        next_x, next_y = self._check_collisions(
            next_x, next_y, next_grid_x, next_grid_y, dx, dy)

        # Aplicar el movimiento final
        if self.map.es_posicion_valida(next_grid_x * self.tile_size, next_grid_y * self.tile_size):
            self.x = next_x
            self.y = next_y
            self.grid_x = next_grid_x
            self.grid_y = next_grid_y
            self.update_rect_position()
            return True
        else:
            # Si la posición no es válida, detener el movimiento
            self.is_moving = False
            self.current_path = []
            return False

    def _detect_collision(self, grid_x, grid_y):
        """Método auxiliar para verificar si una posición de la cuadrícula tiene una colisión"""
        return not self.map.es_posicion_valida(grid_x * self.tile_size, grid_y * self.tile_size)

    def _is_collision_in_vicinity(self, next_grid_x, next_grid_y):
        """Verificar si hay una colisión en las cercanías de la posición de cuadrícula dada"""
        # Comprobar un área de 3x3 alrededor de la posición
        for check_y in range(next_grid_y - 1, next_grid_y + 2):
            for check_x in range(next_grid_x - 1, next_grid_x + 2):
                if self._detect_collision(check_x, check_y):
                    return True
        return False

    def _adjust_movement_for_collision(self, next_x, next_y, next_grid_x, next_grid_y, dx, dy):
        """Ajustar el movimiento cuando se detecta una colisión"""
        if abs(dx) > abs(dy):
            # Intentar moverse solo en dirección X si el movimiento principal es horizontal
            if not self._detect_collision(next_grid_x, self.grid_y):
                return next_x, self.y
            return self.x, self.y
        else:
            # Intentar moverse solo en dirección Y si el movimiento principal es vertical
            if not self._detect_collision(self.grid_x, next_grid_y):
                return self.x, next_y
            return self.x, self.y

    def _check_collisions(self, next_x, next_y, next_grid_x, next_grid_y, dx, dy):
        """Verifica colisiones y ajusta el movimiento en consecuencia"""
        if self._is_collision_in_vicinity(next_grid_x, next_grid_y):
            return self._adjust_movement_for_collision(next_x, next_y, next_grid_x, next_grid_y, dx, dy)
        return next_x, next_y

    def update_direction_from_movement(self, dx, dy):
        """Actualiza la dirección según el movimiento"""
        if dx > 0:
            self.direction = Direction.RIGHT
        elif dx < 0:
            self.direction = Direction.LEFT
        elif dy > 0:
            self.direction = Direction.FRONT
        elif dy < 0:
            self.direction = Direction.BACK
