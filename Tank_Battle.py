"""
    Yuleisy Carmona Vasquez
    22-SISN-2-016
"""
import pygame
import warnings
from Utilidades.Setup import Setup
from Utilidades.Theme import Theme
from Juego.Juego import Juego

# Suppress libpng warnings
warnings.filterwarnings("ignore", category=UserWarning, module='libpng')


def run_game():
    """
    Función para iniciar el juego.
    """
    # Parar la música
    pygame.mixer.music.stop()

    # Iniciar el juego
    juego = Juego()

    # Conectar la detección de colisiones entre el tanque del jugador y el enemigo
    juego.jugador.is_tank_at_position = juego.is_tank_at_position

    # Conectar todos los enemigos
    for enemigo in juego.enemigos:
        # Asignar la función para verificar si una posición está ocupada por un tanque
        enemigo.position_occupied_by_tank = juego.is_tank_at_position
        # Asignar la función para obtener las posiciones de todos los tanques
        enemigo.get_all_tank_positions = juego.get_all_tank_positions

    # Ejecutar el bucle principal del juego
    juego.run()


if __name__ == "__main__":
    # Validar los recursos antes de iniciar el juego
    if not Setup.validate_assets():
        # Salir si los recursos no están disponibles
        exit(1)

    # Inicializar el joystick
    Setup.init_joystick()
    # Inicializar el tema y comenzar el bucle del menú
    surface = Theme.initialize()
    # Pasar la función run_game como callback al menú principal
    Theme.menu_loop(run_game)
