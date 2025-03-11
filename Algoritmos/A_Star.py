"""
    Yuleisy Carmona Vasquez
    22-SISN-2-016
"""

import heapq
from Utilidades.Constantes import CONSTANTES


class AStar:
    def __init__(self, game_map):
        self.map = game_map
        self.tile_size = CONSTANTES.TILE_SIZE.value
        # Almacena la última ruta calculada para visualización
        self.last_path = []
        self.debug_info = {}

    def heuristic(self, a, b):
        """Heurística de distancia Manhattan"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, node, all_occupied_positions=None):
        """Retorna las celdas vecinas válidas"""
        x, y = node
        neighbors = []

        # Convierte occupied_positions a un conjunto para búsqueda más rápida
        occupied_set = set(
            all_occupied_positions) if all_occupied_positions else set()

        # Comprueba las 4 celdas adyacentes
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy

            # Comprueba si la posición está dentro de los límites del mapa
            if not (0 <= nx < self.map.ancho and 0 <= ny < self.map.alto):
                continue

            # Comprueba si la posición es transitable (no es un muro u otro obstáculo)
            if not self.map.es_posicion_valida(nx * self.tile_size, ny * self.tile_size):
                continue

            # Comprueba si la posición está ocupada por otro tanque (excepto el objetivo)
            if (nx, ny) in occupied_set:
                continue

            neighbors.append((nx, ny))

        return neighbors

    def find_path(self, start, goal, all_occupied_positions=None):
        """Encuentra un camino desde el inicio hasta el objetivo utilizando el algoritmo A*"""
        # Si ya estamos en el objetivo, retorna un camino vacío
        if start == goal:
            self.last_path = []
            return []

        # Si el objetivo no es válido, retorna un camino vacío
        if not self.map.es_posicion_valida(goal[0] * self.tile_size, goal[1] * self.tile_size):
            self.last_path = []
            return []

        # Crea un conjunto de posiciones ocupadas (excluyendo inicio y objetivo)
        occupied = []
        if all_occupied_positions:
            occupied = [
                pos for pos in all_occupied_positions if pos != start and pos != goal]

        # Conjunto abierto con nodo inicial
        open_set = []
        heapq.heappush(open_set, (0, start))

        # Diccionario para rastrear de dónde venimos
        came_from = {}

        # Diccionario para g-scores (costo desde el inicio hasta el nodo)
        g_score = {start: 0}

        # Diccionario para f-scores (costo total estimado desde inicio hasta objetivo pasando por el nodo)
        f_score = {start: self.heuristic(start, goal)}

        # Conjunto de nodos visitados
        closed_set = set()

        # Para visualización - almacena nodos explorados
        self.debug_info = {
            'open_set': [],
            'closed_set': [],
            'path': []
        }

        while open_set:
            # Obtiene el nodo con menor f-score
            current_f, current = heapq.heappop(open_set)

            # Añade a datos de visualización
            self.debug_info['open_set'] = [item[1] for item in open_set]

            # Si alcanzamos el objetivo, reconstruye y retorna el camino
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                self.last_path = path
                self.debug_info['path'] = path
                return path

            # Añade el nodo actual al conjunto cerrado
            closed_set.add(current)
            self.debug_info['closed_set'] = list(closed_set)

            # Comprueba todos los vecinos
            for neighbor in self.get_neighbors(current, occupied):
                # Omite si ya fue evaluado
                if neighbor in closed_set:
                    continue

                # Calcula g-score tentativo
                tentative_g_score = g_score.get(current, float('inf')) + 1

                # Si este es un mejor camino al vecino
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    # Actualiza la información del vecino
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + \
                        self.heuristic(neighbor, goal)

                    # Añade al conjunto abierto si no está ya allí
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # Si llegamos aquí, no hay camino posible
        self.last_path = []
        return []

    def get_last_path(self):
        """Retorna la última ruta calculada para visualización"""
        return self.last_path

    def get_debug_info(self):
        """Retorna información de depuración para visualización"""
        return self.debug_info
