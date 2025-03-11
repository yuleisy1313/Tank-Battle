"""
    Yuleisy Carmona Vasquez
    22-SISN-2-016
"""
class Nodo:
    def __init__(self, hijos=None):
        self.hijos = hijos if hijos is not None else []

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

    def ejecutar(self):
        pass


class Selector(Nodo):
    def ejecutar(self):
        # Ejecuta los hijos hasta que uno retorne True
        for hijo in self.hijos:
            if hijo.ejecutar():
                return True
        return False


class Secuencia(Nodo):
    def ejecutar(self):
        # Ejecuta todos los hijos hasta que uno retorne False
        for hijo in self.hijos:
            if not hijo.ejecutar():
                return False
        return True


class Accion(Nodo):
    def __init__(self, accion):
        super().__init__()
        self.accion = accion

    def ejecutar(self):
        return self.accion()


class Timer(Nodo):
    def __init__(self, tiempo):
        super().__init__()
        self.tiempo = tiempo
        self.tiempo_restante = tiempo

    def ejecutar(self):
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            return False
        else:
            self.tiempo_restante = self.tiempo
            # Si no tiene hijos, retorna True. De lo contrario, ejecuta el primer hijo.
            return True if not self.hijos else self.hijos[0].ejecutar()

# Agregar un nuevo tipo de nodo para depuración
class Debug(Nodo):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def ejecutar(self):
        """Para depurar el árbol de comportamiento"""
        print(f"Depuración: {self.message}")
        return True
