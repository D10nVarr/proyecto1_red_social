class Nodo:
    def __init__(self, publicacion):
        self.publicacion= publicacion
        self.siguiente=None
        self.anterior=None

class ListaSimple:#Registro de publicaciones
    def __init__(self):
        self.cabeza = None
        self.total_publicaciones = 0

    def agregar_publicacion(self, publicacion):
        nuevo_nodo = Nodo(publicacion)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente is not None:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
        self.total_publicaciones += 1

    def obtener_publicaciones(self):
        publicaciones = []
        actual = self.cabeza
        while actual is not None:
            publicaciones.append(actual.publicacion)
            actual = actual.siguiente
        return publicaciones

    def buscar_por_palabra(self, palabra_clave):
        resultados = []
        actual = self.cabeza
        while actual is not None:
            if palabra_clave.lower() in actual.publicacion.lower():
                resultados.append(actual.publicacion)
            actual = actual.siguiente
        return resultados


class ListaDoble:#Ir adelante o atras en el feed
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.nodo_actual = None

    def agregar_publicacion(self, publicacion):
        nuevo_nodo = Nodo(publicacion)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
            self.nodo_actual = self.cabeza
        else:
            self.cola.siguiente = nuevo_nodo
            nuevo_nodo.anterior = self.cola
            self.cola = nuevo_nodo

    def ver_siguiente(self):
        if self.nodo_actual is not None and self.nodo_actual.siguiente is not None:
            self.nodo_actual = self.nodo_actual.siguiente
            return self.nodo_actual.publicacion
        return None

    def ver_anterior(self):
        if self.nodo_actual is not None and self.nodo_actual.anterior is not None:
            self.nodo_actual = self.nodo_actual.anterior
            return self.nodo_actual.publicacion
        return None

class ListaCircular:#scroll infinito
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.nodo_actual = None

    def agregar_publicacion(self, publicacion):
        nuevo_nodo = Nodo(publicacion)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
            self.cabeza.siguiente = self.cabeza
            self.nodo_actual = self.cabeza
        else:
            self.cola.siguiente = nuevo_nodo
            nuevo_nodo.siguiente = self.cabeza
            self.cola = nuevo_nodo

    def scroll_infinito(self):
        if self.nodo_actual is not None:
            publicacion_mostrar = self.nodo_actual.publicacion
            self.nodo_actual = self.nodo_actual.siguiente
            return publicacion_mostrar
        return None