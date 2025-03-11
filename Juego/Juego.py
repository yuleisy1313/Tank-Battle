"""
    Yuleisy Carmona Vasquez
    22-SISN-2-016
"""

import pygame
import pygame_menu
from Utilidades.Assets import ASSETS
from Utilidades.Constantes import CONSTANTES, Direction
from Utilidades.Setup import Setup
from Utilidades.Strings import STRINGS
from Utilidades.Theme import Theme
from Juego.Mapa import Mapa
from Entidades.Jugador import Jugador
from Entidades.Misil import Misil
from Entidades.Enemigo import Enemigo, EnemigoState
import random


class Juego:
    def __init__(self):
        # Inicialización de componentes del juego
        self.running = True
        # Actualizar inicialización de la superficie para usar Theme
        self.surface = Theme.initialize()
        pygame.display.set_caption(STRINGS.GAME_TITLE.value)
        self.clock = pygame.time.Clock()

        # Crear mapa del juego
        self.mapa = Mapa()

        # Crear jugador (posición inicial)
        start_x = self.mapa.ancho // 2
        start_y = self.mapa.alto - 2
        self.jugador = Jugador(start_x, start_y, self.mapa,
                               CONSTANTES.TILE_SIZE.value)

        # Lista de misiles
        self.misiles = []

        # Lista de enemigos e inicialización
        self.enemigos = []
        self.max_enemies = 3  # Número máximo de enemigos simultáneos
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 5000  # 5 segundos entre spawns
        self.spawn_initial_enemies()  # Crear enemigos iniciales

        # Estado del juego
        self.score = 0
        self.last_missile_time = 0
        self.missile_cooldown = 500  # milisegundos
        self.game_over = False
        self.game_over_time = 0
        self.game_over_delay = 3000  # 3 segundos de retraso después del game over
        self.victory = False
        self.victory_time = 0
        self.victory_delay = 3000  # 3 segundos de retraso después de la victoria

        # Estado del menú de pausa
        self.paused = False
        # Usar Theme para crear el menú de pausa
        self.pause_menu = Theme.create_pause_menu(
            CONSTANTES.WINDOW_SIZE.value[0],
            CONSTANTES.WINDOW_SIZE.value[1],
            self.unpause_game,
            self.restart_game,
            self.exit_to_main_menu
        )

        # Añadir control para el cooldown de pausa
        self.pause_cooldown = 0
        self.pause_cooldown_time = 300  # milisegundos

        # Configuración de la interfaz de usuario
        self.font_title = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_normal = pygame.font.SysFont('Arial', 24)
        self.font_small = pygame.font.SysFont('Arial', 18)

        # Colores
        self.color_white = (255, 255, 255)
        self.color_red = (255, 50, 50)
        self.color_green = (50, 255, 50)
        self.color_blue = (50, 150, 255)

        # Puntuación y estadísticas del jugador
        self.enemies_destroyed = 0
        self.level = 1

        self.total_enemies_created = 0  # Contador total de enemigos creados
        self.max_total_enemies = 1      # Máximo total de enemigos en el juego

        # Configuración para joystick
        self.joystick = None
        self.init_joystick()
        self.joystick_cooldown = 0
        self.joystick_cooldown_time = 200  # milisegundos entre pulsaciones

        # Añadir el control para el fullscreen
        self.fullscreen_cooldown = 0
        self.fullscreen_cooldown_time = 300  # milisegundos

        # Menús de victoria y derrota
        self.game_over_menu = Theme.create_game_over_menu(
            CONSTANTES.WINDOW_SIZE.value[0],
            CONSTANTES.WINDOW_SIZE.value[1],
            self.restart_game,
            self.exit_to_main_menu,
            self.score,
            self.enemies_destroyed
        )
        self.game_over_menu.disable()

        self.victory_menu = Theme.create_victory_menu(
            CONSTANTES.WINDOW_SIZE.value[0],
            CONSTANTES.WINDOW_SIZE.value[1],
            self.restart_game,
            self.exit_to_main_menu,
            self.score,
            self.enemies_destroyed
        )
        self.victory_menu.disable()

    def init_joystick(self):
        """Inicializa el primer joystick disponible"""
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def spawn_initial_enemies(self):
        """Crea los enemigos iniciales en los puntos de spawn"""
        if len(self.enemigos) >= self.max_enemies:
            return

        spawn_points = self.mapa.get_enemy_spawn_points()
        remaining_slots = self.max_enemies - len(self.enemigos)
        for i in range(min(remaining_slots, len(spawn_points))):
            x, y = spawn_points[i]
            self.crear_enemigo(x, y)

    def crear_enemigo(self, grid_x, grid_y):
        """Crea un nuevo enemigo en la posición especificada si no hay otro tanque allí"""
        # Verificar si la posición es válida y no está ocupada
        if not self.is_tank_at_position(grid_x, grid_y):
            enemigo = Enemigo(grid_x, grid_y, self.mapa,
                              self.jugador, CONSTANTES.TILE_SIZE.value)

            # Asignar directamente métodos para verificar la posición del tanque
            enemigo.get_all_tank_positions = self.get_all_tank_positions

            # Agregar almacenamiento de información de depuración
            enemigo.debug_info = {}

            self.enemigos.append(enemigo)
            return enemigo
        return None

    def get_all_tank_positions(self):
        """Obtener posiciones de todos los tanques en el juego"""
        positions = []
        # Añadir posición del jugador
        positions.append((self.jugador.grid_x, self.jugador.grid_y))
        # Añadir todas las posiciones de los enemigos
        for enemy in self.enemigos:
            positions.append((enemy.grid_x, enemy.grid_y))
        return positions

    def is_tank_at_position(self, grid_x, grid_y):
        """Verificar si hay algún tanque en la posición de cuadrícula especificada"""
        # Verificar posición del jugador
        if self.jugador.grid_x == grid_x and self.jugador.grid_y == grid_y:
            return True

        # Verificar posiciones de enemigos
        for enemy in self.enemigos:
            if enemy.grid_x == grid_x and enemy.grid_y == grid_y:
                return True

        return False

    def check_enemy_spawning(self):
        """Comprueba si se deben generar nuevos enemigos"""
        # Si ya creamos el máximo total de enemigos o tenemos el máximo en pantalla, salimos
        if self.total_enemies_created >= self.max_total_enemies or len(self.enemigos) >= self.max_enemies:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.enemy_spawn_timer <= self.enemy_spawn_delay:
            return

        self.enemy_spawn_timer = current_time
        spawn_points = self.mapa.get_enemy_spawn_points()
        if spawn_points:
            x, y = random.choice(spawn_points)
            if self.crear_enemigo(x, y):
                self.total_enemies_created += 1

    def unpause_game(self):
        """Reanudar el juego"""
        self.paused = False

    def restart_game(self):
        """Reiniciar el juego actual"""
        # Desactivar los menús antes de resetear el juego
        if self.game_over_menu:
            self.game_over_menu.disable()
            self.game_over_menu = None

        if self.victory_menu:
            self.victory_menu.disable()
            self.victory_menu = None

        # Resetear el estado del juego
        self.reset_game()
        self.paused = False

    def exit_to_main_menu(self):
        """Salir al menú principal"""
        # Asegurar que volvemos a modo ventana antes de salir al menú principal
        Theme.ensure_windowed_mode()
        self.running = False

    def toggle_pause(self):
        """Alternar el estado de pausa"""
        # Verificar si el cooldown ha terminado
        current_time = pygame.time.get_ticks()
        if current_time < self.pause_cooldown:
            return

        # Establecer el cooldown para evitar activaciones múltiples rápidas
        self.pause_cooldown = current_time + self.pause_cooldown_time

        self.paused = not self.paused

        # Si se quita la pausa, restablecer el menú de pausa
        if not self.paused:
            self.pause_menu.reset(1)  # Restablecer el estado del menú

    def toggle_victory_menu(self):
        """Activar el menú de victoria si corresponde"""
        if self.victory:
            # Si el menú no existe, crearlo
            if not self.victory_menu:
                self.victory_menu = Theme.create_victory_menu(
                    CONSTANTES.WINDOW_SIZE.value[0],
                    CONSTANTES.WINDOW_SIZE.value[1],
                    self.restart_game,
                    self.exit_to_main_menu,
                    self.score,
                    self.enemies_destroyed
                )

            # Habilitar el menú y actualizar estadísticas
            self.victory_menu.enable()
            self.update_menu_stats(self.victory_menu)

    def toggle_game_over_menu(self):
        """Activar el menú de game over si corresponde"""
        if self.game_over:
            # Si el menú no existe, crearlo
            if not self.game_over_menu:
                self.game_over_menu = Theme.create_game_over_menu(
                    CONSTANTES.WINDOW_SIZE.value[0],
                    CONSTANTES.WINDOW_SIZE.value[1],
                    self.restart_game,
                    self.exit_to_main_menu,
                    self.score,
                    self.enemies_destroyed
                )

            # Habilitar el menú y actualizar estadísticas
            self.game_over_menu.enable()
            self.update_menu_stats(self.game_over_menu)

    def update_menu_stats(self, menu):
        """Actualiza las estadísticas en el menú especificado"""
        # Buscar y actualizar los widgets de estadísticas
        for widget in menu.get_widgets():
            if widget.get_title() != None:
                title = widget.get_title()
                if STRINGS.FINAL_SCORE.value in title:
                    widget.set_title(
                        f"{STRINGS.FINAL_SCORE.value} {self.score}")
                elif STRINGS.FINAL_SCORE_VICTORY.value in title:
                    widget.set_title(
                        f"{STRINGS.FINAL_SCORE_VICTORY.value} {self.score}")
                elif STRINGS.TANKS_DESTROYED.value in title:
                    widget.set_title(
                        f"{STRINGS.TANKS_DESTROYED.value} {self.enemies_destroyed}")
                elif STRINGS.TANKS_DESTROYED_VICTORY.value in title:
                    widget.set_title(
                        f"{STRINGS.TANKS_DESTROYED_VICTORY.value} {self.enemies_destroyed}")

    def handle_events(self):
        """Procesar eventos de entrada"""
        # Procesar eventos básicos (salir del juego)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Detectar pulsación de F11 para cambiar entre pantalla completa y ventana
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    current_time = pygame.time.get_ticks()
                    if current_time > self.fullscreen_cooldown:
                        self.surface = Theme.toggle_fullscreen()
                        self.fullscreen_cooldown = current_time + self.fullscreen_cooldown_time

            # Si estamos en pausa, enviar eventos directamente al menú
            if self.paused and self.pause_menu.is_enabled():
                self.pause_menu.update([event])

        # Verificar pausa con Setup (funciona con teclado y joystick)
        if Setup.is_pause_pressed():
            self.toggle_pause()

        # Verificar disparo con Setup
        if not self.paused and Setup.is_fire_pressed():
            self.fire_missile()

        # Verificar victoria para mostrar el menú de victoria
        if self.victory:
            self.toggle_victory_menu()

        # Verificar game over para mostrar el menú de game over
        if self.game_over:
            self.toggle_game_over_menu()

    def handle_joystick_input(self):
        """Procesa la entrada del joystick para todas las acciones del juego"""
        current_time = pygame.time.get_ticks()

        # Solo procesar botones si no hay enfriamiento activo
        if current_time > self.joystick_cooldown:
            # Botón para disparar (A)
            if self.joystick.get_button(0) and not self.paused:
                self.fire_missile()
                self.joystick_cooldown = current_time + self.joystick_cooldown_time

            # Botón para pausar/despausar (Start)
            if self.joystick.get_button(7):  # Start es generalmente el botón 7
                self.toggle_pause()
                self.joystick_cooldown = current_time + self.joystick_cooldown_time

            # Botón para volver al menú principal (Back/Select)
            # Back/Select es generalmente el botón 6
            if self.joystick.get_button(6):
                if self.paused:
                    self.exit_to_main_menu()
                    self.joystick_cooldown = current_time + self.joystick_cooldown_time

            # Botón para alternar pantalla completa (podríamos usar un botón del joystick)
            # Por ejemplo, usando una combinación como Back+Start para fullscreen
            if self.joystick.get_button(6) and self.joystick.get_button(7):
                self.surface = Theme.toggle_fullscreen()
                self.joystick_cooldown = current_time + self.joystick_cooldown_time

    def fire_missile(self):
        """Crear un nuevo misil basado en la posición y dirección del jugador"""
        # Retornar si el juego ha terminado
        if self.game_over:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_missile_time < self.missile_cooldown:
            return

        self.last_missile_time = current_time

        # Obtener posición del misil según la posición y dirección actual del jugador
        if self.jugador.direction == Direction.FRONT:
            missile_x = self.jugador.grid_x
            missile_y = self.jugador.grid_y + 1
        elif self.jugador.direction == Direction.BACK:
            missile_x = self.jugador.grid_x
            missile_y = self.jugador.grid_y - 1
        elif self.jugador.direction == Direction.RIGHT:
            missile_x = self.jugador.grid_x + 1
            missile_y = self.jugador.grid_y
        else:  # LEFT
            missile_x = self.jugador.grid_x - 1
            missile_y = self.jugador.grid_y

        # Crear misil y añadir a la lista
        missile = Misil(missile_x, missile_y, self.jugador.direction,
                        tile_size=CONSTANTES.TILE_SIZE.value)
        self.misiles.append(missile)

        # Reproducir sonido
        pygame.mixer.Sound.play(pygame.mixer.Sound(
            str(ASSETS.FIRE_SOUND.value)))

    def update(self):
        """Actualizar estado del juego"""
        if self.paused:
            return

        # Verificar fin del juego o victoria
        if self.game_over or self.victory:
            current_time = pygame.time.get_ticks()
            if current_time - (self.game_over_time if self.game_over else self.victory_time) > self.game_over_delay:
                self.reset_game()
            return

        # Verificar condición de victoria
        if len(self.enemigos) == 0 and self.total_enemies_created >= self.max_total_enemies:
            self.victory = True
            self.victory_time = pygame.time.get_ticks()
            pygame.mixer.Sound.play(
                pygame.mixer.Sound(ASSETS.VICTORY_MUSIC.value))
            return

        # Actualizar jugador
        self.jugador.update()

        # Actualizar jugador con entrada de joystick si está disponible
        if self.joystick and not self.jugador.is_moving:
            axis_x = self.joystick.get_axis(0)
            axis_y = self.joystick.get_axis(1)

            # Usar el método existente para mover con joystick si los ejes están fuera de la zona muerta
            if abs(axis_x) > 0.1 or abs(axis_y) > 0.1:
                self.jugador.move_with_joystick(axis_x, axis_y)

        # Actualizar enemigos y manejar disparos de enemigos
        for enemigo in self.enemigos:
            previous_state = enemigo.state

            # Asegurar que el método get_all_tank_positions esté asignado
            if not hasattr(enemigo, 'get_all_tank_positions'):
                enemigo.get_all_tank_positions = self.get_all_tank_positions

            enemigo.update()

            # Verificar si el enemigo debe disparar
            if enemigo.state == EnemigoState.ATTACKING and previous_state != EnemigoState.ATTACKING:
                self.enemy_fire_missile(enemigo)

        # Actualizar misiles
        for missile in self.misiles[:]:
            if not missile.update():
                self.misiles.remove(missile)
                continue

            # Verificar colisión con el mapa
            if missile.collide_with_map(self.mapa):
                # Destruir ladrillo y eliminar misil
                if self.mapa.destruir_bloque(missile.x, missile.y):
                    self.score += 10
                self.misiles.remove(missile)
                continue

            # Verificar colisión de misiles con enemigos
            # Verificación de atributo corregida
            if missile in self.misiles and not getattr(missile, 'is_enemy_missile', False):
                for enemigo in self.enemigos[:]:
                    if missile.rect.colliderect(enemigo.rect):
                        # Eliminar misil
                        if missile in self.misiles:
                            self.misiles.remove(missile)

                        # Aplicar daño al enemigo
                        # 25 de daño por impacto, 2 impactos para destruir
                        if enemigo.take_damage(25):
                            self.enemigos.remove(enemigo)
                            self.enemies_destroyed += 1
                            self.score += 100
                            # Resetear temporizador de spawn cuando un enemigo es destruido
                            self.enemy_spawn_timer = pygame.time.get_ticks()
                        break

            # Verificar colisión de misiles con el jugador (misiles enemigos)
            if getattr(missile, 'is_enemy_missile', False):  # Verificación de atributo corregida
                if missile.rect.colliderect(self.jugador.rect):
                    # Eliminar misil
                    if missile in self.misiles:
                        self.misiles.remove(missile)

                    # Aplicar daño al jugador
                    self.jugador.take_damage(1)  # 1 daño por impacto

                    # Verificar si el jugador está muerto
                    if self.jugador.health <= 0:
                        self.game_over = True
                        self.game_over_time = pygame.time.get_ticks()
                    break

        # Verificar aparición de nuevos enemigos
        self.check_enemy_spawning()

    def enemy_fire_missile(self, enemy):
        """Crear un misil disparado por un enemigo"""
        # Obtener posición del misil según la dirección del enemigo
        grid_x, grid_y = enemy.get_missile_position()

        # Crear misil y marcarlo como misil enemigo
        missile = Misil(grid_x, grid_y, enemy.direction,
                        tile_size=CONSTANTES.TILE_SIZE.value)
        missile.is_enemy_missile = True  # Añadir atributo para rastrear misiles enemigos
        self.misiles.append(missile)

        # Reproducir sonido
        pygame.mixer.Sound.play(pygame.mixer.Sound(ASSETS.FIRE_SOUND.value))

    def render(self):
        """Renderizar el estado del juego"""
        # Obtener la superficie donde renderizar (puede ser diferente en fullscreen)
        render_surface = Theme.get_game_surface()

        # Dibujar mapa
        self.mapa.dibujar(render_surface)

        # Dibujar rutas A* para visualización de depuración - visualizar rutas de enemigos
        for enemigo in self.enemigos:
            if enemigo.current_path:
                self.draw_astar_path(enemigo.current_path,
                                     enemigo, render_surface)

        # Dibujar jugador si no es game over
        if not self.game_over:
            self.jugador.draw(render_surface)

        # Dibujar enemigos
        for enemigo in self.enemigos:
            enemigo.draw(render_surface)

        # Dibujar misiles
        for missile in self.misiles:
            missile.draw(render_surface)

        # Dibujar interfaz de usuario mejorada
        self.render_ui(render_surface)

        # Manejar menú de pausa si está pausado
        if self.paused:
            # Dibujar superposición semitransparente
            overlay = pygame.Surface(
                CONSTANTES.WINDOW_SIZE.value, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Negro semitransparente
            render_surface.blit(overlay, (0, 0))

            # Procesar menú de pausa - no procesamos eventos aquí, ya se hizo en handle_events
            if self.pause_menu and self.pause_menu.is_enabled():
                self.pause_menu.draw(render_surface)

        # Mostrar menú de victoria si corresponde
        elif self.victory:
            # Asegurar que el menú existe antes de usarlo
            self.toggle_victory_menu()

            overlay = pygame.Surface(
                CONSTANTES.WINDOW_SIZE.value, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Negro semitransparente
            render_surface.blit(overlay, (0, 0))

            if self.victory_menu:
                self.victory_menu.draw(render_surface)

        # Mostrar menú de game over si corresponde
        elif self.game_over:
            # Asegurar que el menú existe antes de usarlo
            self.toggle_game_over_menu()

            overlay = pygame.Surface(
                CONSTANTES.WINDOW_SIZE.value, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Negro semitransparente
            render_surface.blit(overlay, (0, 0))

            if self.game_over_menu:
                self.game_over_menu.draw(render_surface)

        # Renderizar a la pantalla real (con escalado si es necesario)
        Theme.render_to_screen()

    def render_ui(self, surface=None):
        """Renderizar la interfaz de usuario con un diseño horizontal en la parte superior"""
        # Usar la superficie proporcionada o la predeterminada
        surface = surface if surface is not None else self.surface

        # Dimensiones y posición de la interfaz
        panel_height = 40
        panel_width = CONSTANTES.WINDOW_SIZE.value[0]
        panel_x = 0
        panel_y = 0

        # Dibujar fondo del panel semitransparente
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))  # Negro semitransparente
        surface.blit(panel, (panel_x, panel_y))

        # Dibujar borde del panel
        pygame.draw.rect(surface, self.color_white,
                         (panel_x, panel_y, panel_width, panel_height), 2)

        # Dibujar título (alineado a la izquierda)
        title = self.font_normal.render(
            STRINGS.GAME_TITLE.value, True, self.color_blue)
        surface.blit(title, (panel_x + 10, panel_y + 10))

        # Calcular posiciones para otros elementos de la interfaz
        score_x = panel_x + 200
        enemies_x = score_x + 150
        destroyed_x = enemies_x + 150

        # Dibujar puntuación
        score_text = self.font_normal.render(
            f"{STRINGS.SCORE_LABEL.value} {self.score}", True, self.color_white)
        surface.blit(score_text, (score_x, panel_y + 10))

        # Dibujar número de enemigos
        enemies_text = self.font_normal.render(
            f"{STRINGS.ENEMIES_LABEL.value} {len(self.enemigos)}", True, self.color_white)
        surface.blit(enemies_text, (enemies_x, panel_y + 10))

        # Dibujar enemigos destruidos
        destroyed_text = self.font_normal.render(
            f"{STRINGS.DESTROYED_LABEL.value} {self.enemies_destroyed}", True, self.color_white)
        surface.blit(destroyed_text, (destroyed_x, panel_y + 10))

        # Dibujar mensaje de victoria o fin del juego
        if self.victory:
            self.toggle_victory_menu()
        elif self.game_over:
            self.toggle_game_over_menu()

    def reset_game(self):
        """Resetear el estado del juego después del fin del juego"""
        # Desactivar los menús antes de resetear el juego
        if self.game_over_menu:
            self.game_over_menu.disable()

        if self.victory_menu:
            self.victory_menu.disable()

        # Resetear el estado del juego
        start_x = self.mapa.ancho // 2
        start_y = self.mapa.alto - 2
        self.jugador = Jugador(start_x, start_y, self.mapa,
                               CONSTANTES.TILE_SIZE.value)

        # Conectar la detección de colisiones de jugador y enemigo
        self.jugador.is_tank_at_position = self.is_tank_at_position

        # Limpiar misiles
        self.misiles.clear()

        # Resetear temporizador de spawn de enemigos
        self.enemy_spawn_timer = pygame.time.get_ticks()

        # Limpiar enemigos y repoblar
        self.enemigos.clear()
        self.spawn_initial_enemies()

        # Resetear puntuación, enemigos destruidos y estado del juego
        self.score = 0
        self.enemies_destroyed = 0  # Resetear contador de enemigos destruidos
        self.game_over = False
        self.victory = False

        self.total_enemies_created = 0  # Resetear contador al reiniciar juego

    def run(self):
        """Bucle principal del juego"""
        while self.running:
            # Recoger todos los eventos una vez por frame
            events = pygame.event.get()

            # Procesar eventos básicos (salir del juego, teclas F11, etc.)
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

                # Detectar pulsación de F11 para cambiar entre pantalla completa y ventana
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        current_time = pygame.time.get_ticks()
                        if current_time > self.fullscreen_cooldown:
                            self.surface = Theme.toggle_fullscreen()
                            self.fullscreen_cooldown = current_time + self.fullscreen_cooldown_time

            # Manejar eventos para los menús de victoria y game over
            if self.game_over:
                # Asegurar que el menú existe
                self.toggle_game_over_menu()
                if self.game_over_menu:
                    self.game_over_menu.update(events)
            elif self.victory:
                # Asegurar que el menú existe
                self.toggle_victory_menu()
                if self.victory_menu:
                    self.victory_menu.update(events)
            # Manejar eventos para el menú de pausa
            elif self.paused and self.pause_menu and self.pause_menu.is_enabled():
                self.pause_menu.update(events)
            # Procesar eventos del juego normal si no está en pausa/victoria/game over
            elif not self.game_over and not self.victory:
                # Verificar pausa con Setup (funciona con teclado y joystick)
                if Setup.is_pause_pressed():
                    self.toggle_pause()

                # Verificar disparo con Setup
                if not self.paused and Setup.is_fire_pressed():
                    self.fire_missile()

            # Actualizar estado del juego si no está en pausa y no es game over/victoria
            if not self.paused and not self.game_over and not self.victory:
                self.update()

            # Siempre renderizar
            self.render()

            # Actualizar estado de entradas para el siguiente frame
            Setup.update_input_states()

            # Mantener el mismo FPS incluso durante la pausa
            self.clock.tick(CONSTANTES.FPS.value)

    def draw_astar_path(self, path, enemy, surface=None):
        """Visualizar la ruta A* para depuración"""
        # Usar la superficie proporcionada o la predeterminada
        surface = surface if surface is not None else self.surface

        if not path:
            return

        # Dibujar ruta como cuadrados rojos transparentes (ruta del enemigo)
        path_surface = pygame.Surface(
            (self.mapa.tile_size, self.mapa.tile_size), pygame.SRCALPHA)

        # Usar diferentes colores para diferentes estados de enemigos
        if enemy.state == EnemigoState.PURSUING:
            # Rojo semitransparente para persecución
            path_surface.fill((255, 0, 0, 100))
        elif enemy.state == EnemigoState.PATROLLING:
            # Azul semitransparente para patrulla
            path_surface.fill((0, 0, 255, 100))
        else:
            # Naranja semitransparente para otros estados
            path_surface.fill((255, 165, 0, 100))

        # Dibujar baldosas de ruta
        for x, y in path:
            surface.blit(
                path_surface, (x * self.mapa.tile_size, y * self.mapa.tile_size))

        # Dibujar conexiones de ruta como líneas
        if len(path) > 1:
            for i in range(len(path) - 1):
                start_pos = (path[i][0] * self.mapa.tile_size + self.mapa.tile_size // 2,
                             path[i][1] * self.mapa.tile_size + self.mapa.tile_size // 2)
                end_pos = (path[i+1][0] * self.mapa.tile_size + self.mapa.tile_size // 2,
                           path[i+1][1] * self.mapa.tile_size + self.mapa.tile_size // 2)
                pygame.draw.line(surface, (255, 255, 255),
                                 start_pos, end_pos, 2)

        # Dibujar marcador en la posición objetivo actual si el enemigo está en movimiento
        if enemy.is_moving:
            target_x = enemy.target_x // self.mapa.tile_size
            target_y = enemy.target_y // self.mapa.tile_size

            target_rect = pygame.Rect(
                target_x * self.mapa.tile_size + 5,
                target_y * self.mapa.tile_size + 5,
                self.mapa.tile_size - 10,
                self.mapa.tile_size - 10
            )
            pygame.draw.rect(surface, (255, 255, 0), target_rect, 2)
