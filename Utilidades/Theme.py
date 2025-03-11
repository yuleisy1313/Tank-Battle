"""
    Yuleisy Carmona Vasquez
    22-SISN-2-016
"""

import pygame as pg
import pygame_menu as pg_menu
from Utilidades.Constantes import CONSTANTES
from Utilidades.Assets import ASSETS
from Utilidades.Strings import STRINGS


class Theme:
    """
    Clase que maneja la interfaz gráfica del menú principal y de las instrucciones

    Attributes
    ----------
    surface : pg.Surface
        Superficie de la ventana del juego
    menu_background_image : pg.Surface
        Imagen de fondo del menú principal
    """
    surface = None
    menu_background_image = None
    is_fullscreen = False  # Variable para rastrear el estado de pantalla completa

    # Variables para mantener la relación de aspecto en modo pantalla completa
    original_size = CONSTANTES.WINDOW_SIZE.value
    game_surface = None  # Surface para renderizar el juego en resolución original
    scale_factor = 1.0   # Factor de escala para mantener relación de aspecto
    render_pos = (0, 0)  # Posición para renderizar con barras negras

    @classmethod
    def initialize(cls):
        """
        Inicializa la ventana del juego y carga la imagen de fondo del menú principal
        """
        pg.display.init()
        cls.surface = pg.display.set_mode(CONSTANTES.WINDOW_SIZE.value)
        cls.menu_background_image = pg.image.load(
            ASSETS.MENU_BACKGROUND.value)
        cls.original_size = CONSTANTES.WINDOW_SIZE.value
        cls.game_surface = pg.Surface(cls.original_size)
        return cls.surface

    @classmethod
    def toggle_fullscreen(cls):
        """
        Cambia entre modo pantalla completa y modo ventana preservando la relación de aspecto
        """
        cls.is_fullscreen = not cls.is_fullscreen

        if cls.is_fullscreen:
            # Cambiar a pantalla completa
            cls.surface = pg.display.set_mode((0, 0), pg.FULLSCREEN)
            cls._calculate_scaling()
        else:
            # Volver a modo ventana con el tamaño original
            cls.surface = pg.display.set_mode(cls.original_size)
            cls.scale_factor = 1.0
            cls.render_pos = (0, 0)

        return cls.surface

    @classmethod
    def _calculate_scaling(cls):
        """
        Calcula el factor de escala y la posición para mantener la relación de aspecto
        en modo pantalla completa usando letterbox/pillarbox.
        """
        # Obtener tamaño de pantalla actual
        screen_width, screen_height = cls.surface.get_size()
        original_width, original_height = cls.original_size

        # Calcular las relaciones de aspecto
        screen_aspect = screen_width / screen_height
        original_aspect = original_width / original_height

        # Calcular factor de escala y posición basado en relación de aspecto
        if screen_aspect > original_aspect:  # Pantalla más ancha que el juego - pillarbox
            cls.scale_factor = screen_height / original_height
            scaled_width = int(original_width * cls.scale_factor)
            cls.render_pos = ((screen_width - scaled_width) // 2, 0)
        else:  # Pantalla más alta que el juego - letterbox
            cls.scale_factor = screen_width / original_width
            scaled_height = int(original_height * cls.scale_factor)
            cls.render_pos = (0, (screen_height - scaled_height) // 2)

    @classmethod
    def get_game_surface(cls):
        """
        Retorna la superficie donde se debe renderizar el juego en resolución original
        """
        if cls.is_fullscreen:
            # En modo fullscreen, se renderiza primero a una superficie de tamaño original
            return cls.game_surface
        else:
            # En modo ventana, se renderiza directamente en la superficie de la ventana
            return cls.surface

    @classmethod
    def render_to_screen(cls):
        """
        Renderiza la superficie del juego a la pantalla, con escalado y barras negras si es necesario
        """
        if cls.is_fullscreen:
            # Llenar la pantalla con negro (para barras letterbox/pillarbox)
            cls.surface.fill((0, 0, 0))

            # Escalar la superficie del juego y dibujarla en la posición correcta
            scaled_width = int(cls.original_size[0] * cls.scale_factor)
            scaled_height = int(cls.original_size[1] * cls.scale_factor)

            # Escalar con alta calidad
            scaled_surface = pg.transform.smoothscale(
                cls.game_surface, (scaled_width, scaled_height))
            cls.surface.blit(scaled_surface, cls.render_pos)

        # Actualizar la pantalla
        pg.display.flip()

    @classmethod
    def ensure_windowed_mode(cls):
        """
        Asegura que el juego esté en modo ventana, útil al volver al menú principal
        """
        if cls.is_fullscreen:
            cls.toggle_fullscreen()
        return cls.surface

    @classmethod
    def main_background(cls):
        """
        Dibuja el fondo del menú cubriendo toda la ventana mediante mosaico
        """
        # Obtener dimensiones
        window_width, window_height = cls.surface.get_rect().size
        image_width, image_height = cls.menu_background_image.get_rect().size

        # Limpiar superficie
        cls.surface.fill(CONSTANTES.COLOR_BLACK.value)

        # Calcular cuántas repeticiones necesitamos
        rows = (window_height + image_height - 1) // image_height
        cols = (window_width + image_width - 1) // image_width

        # Dibujar el fondo en mosaico
        for row in range(rows):
            for col in range(cols):
                x = col * image_width
                y = row * image_height
                cls.surface.blit(cls.menu_background_image, (x, y))

    @staticmethod
    def get_battle_city_theme():
        """
        Crea un tema personalizado para el menú principal del juego Battle City
        """
        return pg_menu.Theme(
            selection_color=CONSTANTES.COLOR_GREEN.value,
            widget_font=CONSTANTES.MENU_FONT.value,
            title_font_size=CONSTANTES.TILE_SIZE.value,
            title_font_color=CONSTANTES.COLOR_GREEN.value,
            title_font=CONSTANTES.MENU_FONT.value,
            widget_font_color=CONSTANTES.COLOR_WHITE.value,
            widget_font_size=CONSTANTES.MENU_FONT_SIZE.value,
            background_color=CONSTANTES.TRANSPARENT_COLOR.value,
            title_background_color=CONSTANTES.TRANSPARENT_COLOR.value,
            widget_margin=(0, 10),
            widget_padding=10
        )

    @classmethod
    def create_about_menu(cls, window_width: int, window_height: int):
        """ 
        Crea un menú con las instrucciones del juego
        """
        theme = cls.get_battle_city_theme()
        about_menu = pg_menu.Menu(
            theme=theme,
            height=window_height,
            width=window_width,
            title=STRINGS.BRIEFING_TITLE.value
        )

        about_menu.add.label(STRINGS.CONTROLS_HEADER.value)
        about_menu.add.label(STRINGS.MOVEMENT_CONTROLS.value)
        about_menu.add.label(STRINGS.FIRE_CONTROLS.value)
        about_menu.add.vertical_margin(25)
        about_menu.add.button(STRINGS.RETURN_BUTTON.value,
                              pg_menu.events.BACK)
        return about_menu

    @classmethod
    def create_credits_menu(cls, window_width: int, window_height: int):
        """ 
        Crea un menú con los créditos del juego
        """
        theme = cls.get_battle_city_theme()
        credits_menu = pg_menu.Menu(
            theme=theme,
            height=window_height,
            width=window_width,
            title=STRINGS.CREDITS_TITLE.value
        )

        credits_menu.add.label(STRINGS.MATERIA.value)
        # Hacer los siguientes labels más pequeños usando el parámetro font_size
        credits_menu.add.label(STRINGS.DEVELOPED_BY.value, font_size=int(
            CONSTANTES.MENU_FONT_SIZE.value * 0.8))
        credits_menu.add.label(STRINGS.MATRICULA.value, font_size=int(
            CONSTANTES.MENU_FONT_SIZE.value * 0.8))
        credits_menu.add.vertical_margin(15)
        credits_menu.add.vertical_margin(25)
        credits_menu.add.button(STRINGS.RETURN_BUTTON.value,
                                pg_menu.events.BACK)
        return credits_menu

    @classmethod
    def create_pause_menu(cls, window_width: int, window_height: int,
                          unpause_callback, restart_callback, exit_callback):
        """
        Crea un menú de pausa para el juego

        Args:
            window_width: Ancho de la ventana
            window_height: Alto de la ventana
            unpause_callback: Función a llamar para reanudar el juego
            restart_callback: Función a llamar para reiniciar el juego
            exit_callback: Función a llamar para salir al menú principal

        Returns:
            pygame_menu.Menu: Menú de pausa configurado
        """
        # Calcular dimensiones del menú
        window_height = int(window_height * 0.6)
        window_width = int(window_width * 0.6)

        # Crear tema y menú
        theme = cls.get_battle_city_theme()
        menu = pg_menu.Menu(
            theme=theme,
            height=window_height,
            width=window_width,
            title=STRINGS.GAME_TITLE.value,
            center_content=True
        )

        # Añadir sonido al menú
        menu_sound = pg_menu.sound.Sound()
        menu_sound.set_sound(
            pg_menu.sound.SOUND_TYPE_WIDGET_SELECTION, ASSETS.CLICK_SOUND.value)
        menu_sound.set_sound(
            pg_menu.sound.SOUND_TYPE_CLICK_MOUSE, ASSETS.FIRE_SOUND.value)
        menu.set_sound(menu_sound)

        # Añadir opciones de menú
        menu.add.button(STRINGS.CONTINUE_BUTTON.value, unpause_callback)
        menu.add.button(STRINGS.RESTART_BUTTON.value, restart_callback)
        menu.add.button(STRINGS.MAIN_MENU_BUTTON.value, exit_callback)

        return menu

    @classmethod
    def create_game_over_menu(cls, window_width: int, window_height: int,
                              restart_callback, exit_callback, score: int, tanks_destroyed: int):
        """
        Crea un menú para la pantalla de Game Over

        Args:
            window_width: Ancho de la ventana
            window_height: Alto de la ventana
            restart_callback: Función para reiniciar el juego
            exit_callback: Función para volver al menú principal
            score: Puntuación final del jugador
            tanks_destroyed: Cantidad de tanques destruidos

        Returns:
            pygame_menu.Menu: Menú de Game Over configurado
        """
        # Calcular dimensiones del menú
        menu_height = int(window_height * 0.6)
        menu_width = int(window_width * 0.6)

        # Crear tema y menú
        theme = cls.get_battle_city_theme()

        menu = pg_menu.Menu(
            theme=theme,
            height=menu_height,
            width=menu_width,
            title=STRINGS.GAME_OVER_TEXT.value,
            center_content=True
        )

        # Añadir sonido al menú
        menu_sound = pg_menu.sound.Sound()
        menu_sound.set_sound(
            pg_menu.sound.SOUND_TYPE_WIDGET_SELECTION, ASSETS.CLICK_SOUND.value)
        menu_sound.set_sound(
            pg_menu.sound.SOUND_TYPE_CLICK_MOUSE, ASSETS.FIRE_SOUND.value)
        menu.set_sound(menu_sound)

        # Añadir elementos al menú - Fuentes reducidas
        menu_font_size = int(CONSTANTES.MENU_FONT_SIZE.value * 0.5)
        menu.add.label(f"{STRINGS.FINAL_SCORE.value} {score}",
                       font_size=menu_font_size, align=pg_menu.locals.ALIGN_CENTER)
        menu.add.label(
            f"{STRINGS.TANKS_DESTROYED.value} {tanks_destroyed}",
            font_size=menu_font_size, align=pg_menu.locals.ALIGN_CENTER)
        menu.add.vertical_margin(30)
        menu.add.button(STRINGS.RESTART_BUTTON.value, restart_callback)
        menu.add.button(STRINGS.MAIN_MENU_BUTTON.value, exit_callback)

        return menu

    @classmethod
    def create_victory_menu(cls, window_width: int, window_height: int,
                            restart_callback, exit_callback, score: int, tanks_destroyed: int):
        """
        Crea un menú para la pantalla de Victoria

        Args:
            window_width: Ancho de la ventana
            window_height: Alto de la ventana
            restart_callback: Función para reiniciar el juego
            exit_callback: Función para volver al menú principal
            score: Puntuación final del jugador
            tanks_destroyed: Cantidad de tanques destruidos

        Returns:
            pygame_menu.Menu: Menú de victoria configurado
        """
        # Calcular dimensiones del menú
        menu_height = int(window_height * 0.6)
        menu_width = int(window_width * 0.6)

        # Crear tema y menú
        theme = cls.get_battle_city_theme()

        menu = pg_menu.Menu(
            theme=theme,
            height=menu_height,
            width=menu_width,
            title=STRINGS.VICTORY_TEXT.value,
            center_content=True
        )

        # Añadir sonido al menú
        menu_sound = pg_menu.sound.Sound()
        menu_sound.set_sound(
            pg_menu.sound.SOUND_TYPE_WIDGET_SELECTION, ASSETS.CLICK_SOUND.value)
        menu_sound.set_sound(
            pg_menu.sound.SOUND_TYPE_CLICK_MOUSE, ASSETS.FIRE_SOUND.value)
        menu.set_sound(menu_sound)

        # Añadir elementos al menú - Fuentes reducidas
        menu_font_size = int(CONSTANTES.MENU_FONT_SIZE.value * 0.5)
        menu.add.label(
            f"{STRINGS.FINAL_SCORE_VICTORY.value} {score}",
            font_size=menu_font_size, align=pg_menu.locals.ALIGN_CENTER)
        menu.add.label(
            f"{STRINGS.TANKS_DESTROYED_VICTORY.value} {tanks_destroyed}",
            font_size=menu_font_size, align=pg_menu.locals.ALIGN_CENTER)
        menu.add.vertical_margin(30)
        menu.add.button(STRINGS.RESTART_BUTTON.value, restart_callback)
        menu.add.button(STRINGS.MAIN_MENU_BUTTON.value, exit_callback)

        return menu

    @classmethod
    def menu_loop(cls, run_game):
        """
        Método de clase que implementa el bucle principal del menú del juego.

        Este método inicializa y controla toda la interfaz del menú principal,
        incluyendo la música de fondo, los efectos de sonido, y la navegación
        entre las diferentes opciones de menú.

        Parámetros:
        -----------
        run_game : callable
            Función o método que se invocará cuando el usuario seleccione 
            la opción de iniciar el juego. Esta función debe contener toda 
            la lógica necesaria para comenzar la partida.

        Flujo de ejecución:
        ------------------
        1. Inicializa Pygame y el sistema de sonido
        2. Configura y reproduce la música de fondo en bucle infinito
        3. Establece el título de la ventana del juego
        4. Configura el reloj para controlar la frecuencia de actualización
        5. Configura los efectos de sonido para la interacción con el menú
        6. Calcula las dimensiones de la ventana del juego
        7. Crea el submenú "Acerca de" (briefing)
        8. Establece el tema visual del menú
        9. Crea el menú principal con sus botones
        10. Vincula los sonidos a ambos menús
        11. Ejecuta el bucle principal que mantiene el menú activo
        12. Cierra el programa cuando el usuario sale del menú

        Características implementadas:
        ----------------------------
        - Música de fondo que se reproduce continuamente
        - Efectos de sonido para la selección y clic en elementos del menú
        - Menú principal con opciones para: iniciar juego, ver briefing y salir
        - Submenú con información adicional sobre el juego
        - Control de tasa de refresco (FPS) para mantener consistencia
        - Gestión apropiada de eventos de cierre

        Dependencias:
        -----------
        - pygame (pg): Para la gestión de gráficos, sonidos y eventos
        - pygame_menu (pg_menu): Para la creación y gestión de menús
        - ASSETS: Enumeración con rutas a recursos como música y sonidos
        - STRINGS: Enumeración con textos localizados para el menú
        - CONSTANTES: Enumeración con valores de configuración del juego
        """

        # Inicialización de Pygame y sistema de audio
        pg.init()
        pg.mixer.init()
        # Carga la música de fondo
        pg.mixer.music.load(ASSETS.BACKGROUND_MUSIC.value)
        pg.mixer.music.play(-1)  # Reproduce en bucle infinito (-1)

        # Configuración de la ventana de juego
        # Establece el título de la ventana
        pg.display.set_caption(STRINGS.GAME_TITLE.value)
        clock = pg.time.Clock()  # Inicializa el reloj para controlar FPS

        # Configuración de efectos de sonido para el menú
        menu_sound = pg_menu.sound.Sound()
        menu_sound.set_sound(pg_menu.sound.SOUND_TYPE_WIDGET_SELECTION,
                             ASSETS.FIRE_SOUND.value)  # Sonido al navegar entre opciones
        menu_sound.set_sound(pg_menu.sound.SOUND_TYPE_CLICK_MOUSE,
                             ASSETS.CLICK_SOUND.value)  # Sonido al hacer clic

        # Cálculo de las dimensiones de la ventana según escala configurada
        window_height = int(
            CONSTANTES.WINDOW_SIZE.value[1] * CONSTANTES.WINDOW_SCALE.value)
        window_width = int(
            CONSTANTES.WINDOW_SIZE.value[0] * CONSTANTES.WINDOW_SCALE.value)

        # Creación del submenú "Acerca de"
        about_menu = cls.create_about_menu(window_width, window_height)

        # Creación del submenú "Créditos"
        credits_menu = cls.create_credits_menu(window_width, window_height)

        # Configuración del tema visual del menú
        theme = cls.get_battle_city_theme()

        # Creación del menú principal
        main_menu = pg_menu.Menu(
            theme=theme,
            height=window_height,
            width=window_width,
            onclose=pg_menu.events.EXIT,  # Acción al cerrar el menú (salir)
            title=f'   {STRINGS.GAME_TITLE.value}'  # Título del menú
        )

        # Añadir botones al menú principal
        main_menu.add.button(STRINGS.START_BUTTON.value,
                             run_game)  # Botón para iniciar juego
        main_menu.add.button(STRINGS.BRIEFING_BUTTON.value,
                             about_menu)  # Botón para ver briefing
        main_menu.add.button("Créditos",
                             credits_menu)  # Botón para ver créditos
        main_menu.add.button(STRINGS.RETREAT_BUTTON.value,
                             pg_menu.events.EXIT)  # Botón para salir

        # Asignar los efectos de sonido a ambos menús
        main_menu.set_sound(menu_sound)
        about_menu.set_sound(menu_sound)
        credits_menu.set_sound(menu_sound)

        # Bucle principal del menú
        running = True
        while running:
            clock.tick(CONSTANTES.FPS.value)  # Controla la tasa de refresco
            cls.main_background()  # Dibuja el fondo del menú

            # Gestión de eventos de Pygame
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:  # Si se cierra la ventana
                    running = False  # Termina el bucle
                elif event.type == pg.KEYDOWN and event.key == pg.K_F11:
                    cls.toggle_fullscreen()  # Cambia entre pantalla completa y ventana

            # Si el menú principal está activo, ejecuta su bucle interno
            if main_menu.is_enabled():
                main_menu.mainloop(cls.surface, cls.main_background)

            # Actualiza la pantalla
            pg.display.flip()

        # Asegura que el juego esté en modo ventana al salir
        cls.ensure_windowed_mode()

        # Cierra el programa cuando se sale del bucle
        exit()

    @staticmethod
    def load_game_background(tile_size):
        """Carga la imagen de fondo del menu principal"""
        background_image = pg.image.load(
            ASSETS.GAME_BACKGROUND.value).convert()
        return pg.transform.scale(background_image, (tile_size, tile_size))

    @staticmethod
    def draw_background(surface, background_image, tile_size, window_size):
        """Dibuja el fondo del juego"""
        for y in range(0, window_size[1], tile_size):
            for x in range(0, window_size[0], tile_size):
                surface.blit(background_image, (x, y))

    @classmethod
    def get_current_surface(cls):
        """
        Devuelve la superficie actual para renderizar, que puede ser la superficie del juego
        en modo pantalla completa o la superficie de la ventana en modo ventana.

        Este método es útil para los menús que deben saber dónde dibujar.
        """
        return cls.game_surface if cls.is_fullscreen else cls.surface
