import json
import os
from datetime import datetime
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


class GestorPublicaciones:
    def __init__(self, lista_simple, lista_doble, lista_circular):
        # Conectamos las estructuras
        self.lista_simple = lista_simple
        self.lista_doble = lista_doble
        self.lista_circular = lista_circular

        self.archivo_datos = "red_social_data.json"
        self.modo_circular = False

    # --- Persistencia JSON ---
    def guardar_datos(self):
        datos = []
        actual = self.lista_simple.cabeza
        while actual:
            datos.append(actual.publicacion)
            actual = actual.siguiente

        try:
            with open(self.archivo_datos, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar archivo: {e}")

    def cargar_datos(self):
        """Carga el JSON y reconstruye las listas al iniciar."""
        if not os.path.exists(self.archivo_datos):
            return

        try:
            with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                datos_cargados = json.load(f)
                for item in datos_cargados:
                    # Cargamos sin volver a guardar para no entrar en bucle
                    self.crear_nueva_publicacion(item['contenido'], item, guardar=False)
        except Exception as e:
            print(f"Error al cargar archivo: {e}")
    #Funcionalidades Principales
    def crear_nueva_publicacion(self, texto, datos_preexistentes=None, guardar=True):
        if datos_preexistentes:
            pub = datos_preexistentes
        else:
            pub = {
                "id": self.lista_simple.total_publicaciones + 1,
                "contenido": texto,
                "likes": 0,
                "comentarios": [],
                "favorito": False,
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
        self.lista_simple.agregar_publicacion(pub)
        self.lista_doble.agregar_publicacion(pub)
        self.lista_circular.agregar_publicacion(pub)

        if guardar:
            self.guardar_datos()
        return pub

    #Navegación
    def cambiar_modo_circular(self, activo):
        self.modo_circular = activo

    def ir_siguiente(self):
        if self.modo_circular:
            return self.lista_circular.scroll_infinito()
        return self.lista_doble.ver_siguiente()

    def ir_anterior(self):
        #Solo la lista doble permite retroceder según el código
        return self.lista_doble.ver_anterior()

    #Interacciones y Estadísticas---
    def buscar(self, palabra):
        return self.lista_simple.buscar_por_palabra(palabra)

    def dar_like(self, pub_id):
        actual = self.lista_simple.cabeza
        while actual:
            if actual.publicacion['id'] == pub_id:
                actual.publicacion['likes'] += 1
                self.guardar_datos()
                return True
            actual = actual.siguiente
        return False

    def agregar_comentario(self, pub_id, texto):
        actual = self.lista_simple.cabeza
        while actual:
            if actual.publicacion['id'] == pub_id:
                actual.publicacion['comentarios'].append(texto)
                self.guardar_datos()
                return True
            actual = actual.siguiente
        return False

    def calcular_estadisticas(self):
        total_l = 0
        total_c = 0
        todas = []

        actual = self.lista_simple.cabeza
        while actual:
            p = actual.publicacion
            total_l += p['likes']
            total_c += len(p['comentarios'])
            todas.append(p)
            actual = actual.siguiente

        ranking = sorted(todas, key=lambda x: x['likes'], reverse=True)
        return {
            "likes_totales": total_l,
            "comentarios_totales": total_c,
            "top_populares": ranking[:3]
        }