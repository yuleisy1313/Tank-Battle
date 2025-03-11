"""
    Yuleisy Carmona Vasquez
    22-SISN-2-016
"""

from enum import Enum

class STRINGS (Enum):
    '''
    Textos que utiliza el juego centralizado en una misma clase
    '''

    # * Títulos
    GAME_TITLE = 'TANK BATTLE'
    BRIEFING_TITLE = 'INSTRUCCIONES'

    # * Menú Principal
    START_BUTTON = 'INICIAR MISIÓN'
    BRIEFING_BUTTON = 'INSTRUCCIONES'
    CREDITS_BUTTON = 'CRÉDITOS'
    RETREAT_BUTTON = 'RETIRADA'
    RETURN_BUTTON = 'VOLVER AL CUARTEL'

    # * Créditos
    CREDITS_TITLE = 'CRÉDITOS'
    DEVELOPED_BY = 'Yuleisy Carmona Vasquez'
    MATRICULA = '22-SISN-2-016'
    MATERIA= 'Inteligencia Artificial'

    # * Menú de Pausa
    CONTINUE_BUTTON = 'Continuar'
    RESTART_BUTTON = 'Reiniciar'
    MAIN_MENU_BUTTON = 'Menú'
    PAUSED_TITLE = 'Juego Pausado'

    # * Controles
    CONTROLS_HEADER = 'CONTROLES:'
    MOVEMENT_CONTROLS = 'MOVIMIENTO: FLECHAS'
    FIRE_CONTROLS = 'DISPARAR: ESPACIO'
    PAUSE_CONTROLS = 'PAUSA: ESC'

    # * UI del Juego
    SCORE_LABEL = 'Puntos:'
    HEALTH_LABEL = 'Vida:'
    ENEMIES_LABEL = 'Enemigos:'
    DESTROYED_LABEL = 'Destruidos:'

    # * Game Over
    GAME_OVER_TEXT = 'Derrota'
    FINAL_SCORE = 'Puntos totales:'
    TANKS_DESTROYED = 'Tanques destruidos:'
    RESTARTING = 'Reiniciando...'

    # * Game Win
    GAME_WIN_TEXT = '¡Misión completada!'
    FINAL_SCORE_WIN = 'Puntos totales:'
    TANKS_DESTROYED_WIN = 'Tanques destruidos:'
    PLAY_AGAIN = 'Presiona ESPACIO para jugar de nuevo'

    # * Victory Screen
    VICTORY_TEXT = '¡Victoria!'
    FINAL_SCORE_VICTORY = 'Puntuación Final:'
    TANKS_DESTROYED_VICTORY = 'Tanques Eliminados:'
    CONTINUE_TEXT = 'Presiona ESPACIO para continuar'

