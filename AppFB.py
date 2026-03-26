import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import os

# ---BACKEND ---
try:
    from FaceBook2 import ListaSimple, ListaDoble, ListaCircular, GestorPublicaciones
except ImportError:
    messagebox.showerror("Error Crítico", "No se encontró FaceBook2.py en esta carpeta.")

# --CONSTANTES DE COLOR--
BG_MAIN = "#0b141d"
BG_CARD = "#151f2b"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#8899a6"
ACCENT_PURPLE = "#3d0245"
HOVER_PURPLE = "#5a0466"
BORDER_COLOR = "#2f3336"


# --GESTIÓN DE ARCHIVOS--
def cargar_json(archivo, defecto):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r") as f:
                return json.load(f)
        except:
            return defecto
    return defecto


class EvilFaceBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EVIL FACEBOOK Pro - Extreme Edition")

        self.root.geometry("900x600")
        try:
            self.root.state('zoomed')
        except:
            self.root.attributes('-fullscreen', True)

        self.root.configure(bg=BG_MAIN)

        self.ls, self.ld, self.lc = ListaSimple(), ListaDoble(), ListaCircular()
        self.gestor = GestorPublicaciones(self.ls, self.ld, self.lc)
        self.gestor.cargar_datos()

        self.usuarios = cargar_json("usuarios.json", {"aki": "1234"})
        if isinstance(self.usuarios, list):
            self.usuarios = {u: "1234" for u in self.usuarios}

        self.amigos = cargar_json("amigos.json", {})
        self.solicitudes = cargar_json("solicitudes.json", {})

        self.favoritos = cargar_json("favoritos.json", {})

        self.user_session = None
        self.temp_img_path = None
        self.current_view = "global"
        self.target_user = None

        #  Feed Dinámico
        self.modo_circular = False
        self.nodo_actual = None

        # Variables para el auto-play ---
        self.auto_play_activo = False
        self.auto_play_id = None

        self.pantalla_login()

    def guardar_todo(self):
        with open("usuarios.json", "w") as f: json.dump(self.usuarios, f)
        with open("amigos.json", "w") as f: json.dump(self.amigos, f)
        with open("solicitudes.json", "w") as f: json.dump(self.solicitudes, f)
        with open("favoritos.json", "w") as f: json.dump(self.favoritos, f)
        self.gestor.guardar_datos()

    # ---LOGIN ---
    def pantalla_login(self):
        for w in self.root.winfo_children(): w.destroy()
        f = tk.Frame(self.root, bg=BG_MAIN)
        f.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(f, text="EVIL FACEBOOK", fg=TEXT_PRIMARY, bg=BG_MAIN, font=("Segoe UI", 45, "bold")).pack()

        self.ent_user = tk.Entry(f, bg=BG_CARD, fg="white", insertbackground="white", font=("Segoe UI", 12), bd=0,
                                 justify="center")
        self.ent_user.pack(ipady=10, ipadx=30, pady=(20, 10))
        self.ent_user.insert(0, "aki")

        self.ent_pass = tk.Entry(f, bg=BG_CARD, fg="white", insertbackground="white", font=("Segoe UI", 12), bd=0,
                                 justify="center", show="*")
        self.ent_pass.pack(ipady=10, ipadx=30, pady=(0, 20))
        self.ent_pass.insert(0, "1234")

        self.crear_boton(f, "ENTRAR", self.intentar_login, width=25).pack(pady=5)
        self.crear_boton(f, "REGISTRAR", self.registrar_usuario, bg="#1a1a1a", width=25).pack()

    def intentar_login(self):
        u = self.ent_user.get().lower().strip()
        p = self.ent_pass.get().strip()

        if u in self.usuarios and self.usuarios[u] == p:
            self.user_session = u
            self.nodo_actual = self.gestor.lista_doble.cabeza
            self.mostrar_interfaz("global")
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    def registrar_usuario(self):
        u = self.ent_user.get().lower().strip()
        p = self.ent_pass.get().strip()

        if not u or not p:
            messagebox.showwarning("!", "Por favor, llene ambos campos.")
            return

        if u not in self.usuarios:
            self.usuarios[u] = p
            self.guardar_todo()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
        else:
            messagebox.showwarning("!", "El usuario ya existe.")


    def mostrar_interfaz(self, vista, parametro=None):

        if hasattr(self, "auto_play_id") and self.auto_play_id:
            self.root.after_cancel(self.auto_play_id)
            self.auto_play_id = None
        if vista != "global":
            self.auto_play_activo = False

        pos_scroll = self.canvas.yview()[0] if hasattr(self, 'canvas') and self.canvas.winfo_exists() else 0

        if vista == "global" and self.current_view != "global":
            self.nodo_actual = self.gestor.lista_doble.cabeza

        for w in self.root.winfo_children(): w.destroy()
        self.current_view = vista
        self.target_user = parametro

        # Header
        header = tk.Frame(self.root, bg=BG_MAIN, height=60, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill="x")
        tk.Label(header, text=f"EVIL FACEBOOK // {vista.upper()}", fg=TEXT_PRIMARY, bg=BG_MAIN,
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=25, pady=15)
        self.crear_boton(header, "SALIR", self.pantalla_login, bg="#450202").pack(side="right", padx=20)

        # Layout
        main_body = tk.Frame(self.root, bg=BG_MAIN)
        main_body.pack(fill="both", expand=True, padx=25, pady=20)

        # Sidebar
        sidebar = tk.Frame(main_body, bg=BG_MAIN, width=250)
        sidebar.pack(side="left", fill="y", padx=(0, 20))

        s_card = tk.Frame(sidebar, bg=BG_CARD, padx=15, pady=15)
        s_card.pack(fill="x")
        tk.Label(s_card, text=f"@{self.user_session}", fg=TEXT_PRIMARY, bg=BG_CARD, font=("Segoe UI", 11, "bold")).pack(
            anchor="w")

        # CONTADOR TOTAL DE PUBLICACIONES
        total_pubs = len(self.gestor.lista_simple.obtener_publicaciones())
        tk.Label(s_card, text=f"Total de posts en la red: {total_pubs}", fg="#28a745", bg=BG_CARD,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(5, 0))

        self.crear_boton(s_card, "FEED DINÁMICO", lambda: self.mostrar_interfaz("global")).pack(fill="x", pady=(15, 5))
        self.crear_boton(s_card, "MI PERFIL", lambda: self.mostrar_interfaz("perfil", self.user_session)).pack(fill="x",
                                                                                                               pady=5)

        self.crear_boton(s_card, "⭐ FAVORITOS", lambda: self.mostrar_interfaz("favoritos")).pack(fill="x", pady=5)

        self.crear_boton(s_card, "AMIGOS", lambda: self.mostrar_interfaz("amigos")).pack(fill="x", pady=5)
        self.crear_boton(s_card, "SOLICITUDES", lambda: self.mostrar_interfaz("solicitudes")).pack(fill="x", pady=5)


        self.crear_boton(s_card, "📊 ESTADÍSTICAS / RANKING", lambda: self.mostrar_interfaz("estadisticas"),
                         bg="#d9534f").pack(fill="x", pady=(15, 5))


        tk.Label(sidebar, text="BUSCAR USUARIO", fg=TEXT_SECONDARY, bg=BG_MAIN, font=("Segoe UI", 7, "bold")).pack(
            pady=(20, 5), anchor="w")
        ent_bus = tk.Entry(sidebar, bg=BG_CARD, fg="white", bd=0)
        ent_bus.pack(fill="x", ipady=8)
        self.crear_boton(sidebar, "VER PERFIL", lambda: self.mostrar_interfaz("perfil", ent_bus.get().lower())).pack(
            pady=5, fill="x")


        tk.Label(sidebar, text="BUSCAR POR PALABRA CLAVE", fg=TEXT_SECONDARY, bg=BG_MAIN,
                 font=("Segoe UI", 7, "bold")).pack(pady=(20, 5), anchor="w")
        ent_bus_pal = tk.Entry(sidebar, bg=BG_CARD, fg="white", bd=0)
        ent_bus_pal.pack(fill="x", ipady=8)
        self.crear_boton(sidebar, "BUSCAR POSTS", lambda: self.mostrar_interfaz("buscar", ent_bus_pal.get())).pack(
            pady=5, fill="x")


        self.area_feed = tk.Frame(main_body, bg=BG_MAIN)
        self.area_feed.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(self.area_feed, bg=BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.area_feed, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=BG_MAIN)

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=800)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


        if vista == "global":
            self.render_feed()
        elif vista == "perfil":
            self.render_perfil(parametro)
        elif vista == "amigos":
            self.render_amigos()
        elif vista == "solicitudes":
            self.render_solicitudes()
        elif vista == "buscar":
            self.render_buscar(parametro)
        # --- NUEVO: Renderizados extra ---
        elif vista == "favoritos":
            self.render_favoritos()
        elif vista == "estadisticas":
            self.render_estadisticas()

        self.root.update_idletasks()
        if vista != "global": self.canvas.yview_moveto(pos_scroll)


        if vista == "global" and self.auto_play_activo:
            self.auto_play_id = self.root.after(3000, self.post_siguiente)


    def render_feed(self):
        comp = tk.Frame(self.scroll_frame, bg=BG_CARD, padx=20, pady=20, highlightthickness=1,
                        highlightbackground=BORDER_COLOR)
        comp.pack(fill="x", pady=(0, 20))
        self.ent_post = tk.Entry(comp, bg=BG_MAIN, fg="white", bd=0, font=("Segoe UI", 11))
        self.ent_post.pack(fill="x", ipady=15, pady=10)

        bb = tk.Frame(comp, bg=BG_CARD)
        bb.pack(fill="x")
        self.btn_img = self.crear_boton(bb, "📷 IMAGEN", self.subir_foto, bg="#1d2125")
        self.btn_img.pack(side="left")
        self.crear_boton(bb, "PUBLICAR", self.postear).pack(side="right")

        ctrl = tk.Frame(self.scroll_frame, bg=BG_MAIN)
        ctrl.pack(fill="x", pady=10)


        f_modos = tk.Frame(ctrl, bg=BG_MAIN)
        f_modos.pack()

        texto_modo = "🔄 MODO CIRCULAR: ACTIVADO" if self.modo_circular else "➡ MODO NORMAL: ACTIVADO"
        color_modo = "#0056b3" if self.modo_circular else TEXT_SECONDARY
        self.crear_boton(f_modos, texto_modo, self.toggle_circular, bg=color_modo, width=30).pack(side="left", padx=5,
                                                                                                  pady=10)

        texto_auto = "⏸ DETENER AUTO-PLAY" if self.auto_play_activo else "▶ INICIAR AUTO-PLAY (3s)"
        color_auto = "#d9534f" if self.auto_play_activo else "#28a745"
        self.crear_boton(f_modos, texto_auto, self.toggle_autoplay, bg=color_auto, width=25).pack(side="left", padx=5,
                                                                                                  pady=10)


        nav = tk.Frame(ctrl, bg=BG_MAIN)
        nav.pack()
        self.crear_boton(nav, "◀ ANTERIOR", self.post_anterior, bg="#1a1a1a").pack(side="left", padx=10)
        self.crear_boton(nav, "SIGUIENTE ▶", self.post_siguiente, bg="#1a1a1a").pack(side="right", padx=10)

        if not self.nodo_actual:
            self.nodo_actual = self.gestor.lista_doble.cabeza

        if self.nodo_actual:
            self.crear_card(self.nodo_actual.publicacion)
        else:
            tk.Label(self.scroll_frame, text="No hay publicaciones en la red.", fg=TEXT_SECONDARY, bg=BG_MAIN).pack(
                pady=40)


    def render_favoritos(self):
        f = tk.Frame(self.scroll_frame, bg=BG_CARD, padx=20, pady=20)
        f.pack(fill="x", pady=(0, 20))
        tk.Label(f, text="⭐ Tus Favoritos", fg="#f1c40f", bg=BG_CARD, font=("Segoe UI", 16, "bold")).pack(side="left")

        mis_favs = self.favoritos.get(self.user_session, [])
        todas_las_pubs = self.gestor.lista_simple.obtener_publicaciones()

        encontradas = False
        for p in todas_las_pubs[::-1]:
            if p.get('id') in mis_favs:
                self.crear_card(p)
                encontradas = True

        if not encontradas:
            tk.Label(self.scroll_frame, text="Aún no tienes publicaciones favoritas.", fg=TEXT_SECONDARY,
                     bg=BG_MAIN).pack(pady=40)

    def render_estadisticas(self):
        f = tk.Frame(self.scroll_frame, bg=BG_CARD, padx=20, pady=20)
        f.pack(fill="x", pady=(0, 20))
        tk.Label(f, text="📊 Estadísticas de Uso y Ranking", fg=TEXT_PRIMARY, bg=BG_CARD,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")

        todas_las_pubs = self.gestor.lista_simple.obtener_publicaciones()
        total_likes = sum(p.get("likes", 0) for p in todas_las_pubs)
        total_comentarios = sum(len(p.get("comentarios", [])) for p in todas_las_pubs)

        stats = tk.Frame(self.scroll_frame, bg=BG_MAIN)
        stats.pack(fill="x", pady=10)
        tk.Label(stats, text=f"Publicaciones Totales: {len(todas_las_pubs)}", fg=TEXT_PRIMARY, bg=BG_MAIN,
                 font=("Segoe UI", 12)).pack(anchor="w")
        tk.Label(stats, text=f"Likes Globales: {total_likes}", fg="#ff4500", bg=BG_MAIN, font=("Segoe UI", 12)).pack(
            anchor="w")
        tk.Label(stats, text=f"Comentarios Totales: {total_comentarios}", fg="#0056b3", bg=BG_MAIN,
                 font=("Segoe UI", 12)).pack(anchor="w")

        tk.Label(self.scroll_frame, text="🏆 TOP 3 PUBLICACIONES:", fg="#f1c40f", bg=BG_MAIN,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(30, 10))

        ranking = sorted(todas_las_pubs, key=lambda x: x.get('likes', 0), reverse=True)[:3]
        for i, p in enumerate(ranking):
            tk.Label(self.scroll_frame, text=f"#{i + 1} con {p.get('likes', 0)} Likes", fg=TEXT_PRIMARY, bg=BG_MAIN,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            self.crear_card(p)


    def render_buscar(self, palabra):
        f = tk.Frame(self.scroll_frame, bg=BG_CARD, padx=20, pady=20)
        f.pack(fill="x", pady=(0, 20))
        tk.Label(f, text=f"Resultados para: '{palabra}'", fg=TEXT_PRIMARY, bg=BG_CARD,
                 font=("Segoe UI", 16, "bold")).pack(side="left")


        todas_las_pubs = self.gestor.lista_simple.obtener_publicaciones()
        resultados = []
        for p in todas_las_pubs:
            if palabra.lower() in p.get("contenido", "").lower():
                resultados.append(p)

        if resultados:
            for p in resultados[::-1]:
                self.crear_card(p)
        else:
            tk.Label(self.scroll_frame, text="No se encontraron coincidencias.", fg=TEXT_SECONDARY, bg=BG_MAIN).pack(
                pady=40)

    def render_perfil(self, user):
        f = tk.Frame(self.scroll_frame, bg=BG_CARD, padx=20, pady=20)
        f.pack(fill="x", pady=(0, 20))
        tk.Label(f, text=f"Perfil de @{user}", fg=TEXT_PRIMARY, bg=BG_CARD, font=("Segoe UI", 16, "bold")).pack(
            side="left")

        if user != self.user_session:
            self.crear_boton(f, "+ ENVIAR SOLICITUD", lambda: self.enviar_soli(user)).pack(side="right")

        pubs = self.gestor.lista_simple.obtener_publicaciones()
        for p in pubs[::-1]:
            if p["contenido"].startswith(f"{user}:"): self.crear_card(p)

    def render_amigos(self):
        lista = self.amigos.get(self.user_session, [])
        for am in lista:
            f = tk.Frame(self.scroll_frame, bg=BG_CARD, padx=15, pady=10)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=f"@{am}", fg=TEXT_PRIMARY, bg=BG_CARD).pack(side="left")
            self.crear_boton(f, "VER", lambda a=am: self.mostrar_interfaz("perfil", a)).pack(side="right")

    def render_solicitudes(self):
        recibidas = self.solicitudes.get(self.user_session, {}).get("recibidas", [])
        for r in recibidas:
            f = tk.Frame(self.scroll_frame, bg=BG_CARD, padx=15, pady=10)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=f"@{r} quiere ser tu amigo", fg=TEXT_PRIMARY, bg=BG_CARD).pack(side="left")
            self.crear_boton(f, "ACEPTAR", lambda x=r: self.aceptar_soli(x), bg="#28a745").pack(side="right", padx=5)


    def toggle_circular(self):
        self.modo_circular = not self.modo_circular
        self.mostrar_interfaz("global")


    def toggle_autoplay(self):
        self.auto_play_activo = not self.auto_play_activo
        self.mostrar_interfaz("global")

    def post_siguiente(self):
        if not self.nodo_actual: return

        if self.modo_circular:
            if self.nodo_actual.siguiente:
                self.nodo_actual = self.nodo_actual.siguiente
            else:
                self.nodo_actual = self.gestor.lista_doble.cabeza
        else:
            if self.nodo_actual.siguiente:
                self.nodo_actual = self.nodo_actual.siguiente
            else:
                # --- MODIFICADO PARA AUTOPLAY ---
                if self.auto_play_activo:
                    self.auto_play_activo = False
                else:
                    messagebox.showinfo("Fin del Feed", "Has llegado al final de las publicaciones.")

        self.mostrar_interfaz("global")

    def post_anterior(self):
        if not self.nodo_actual: return

        if self.nodo_actual.anterior:
            self.nodo_actual = self.nodo_actual.anterior
        else:
            if self.modo_circular:
                temp = self.gestor.lista_doble.cabeza
                while temp and temp.siguiente:
                    temp = temp.siguiente
                self.nodo_actual = temp
            else:
                messagebox.showinfo("Inicio", "Estás en la primera publicación.")

        self.mostrar_interfaz("global")

    def subir_foto(self):
        self.temp_img_path = filedialog.askopenfilename()
        if self.temp_img_path: self.btn_img.config(text="✔ LISTA")

    def postear(self):
        t = self.ent_post.get()
        if t:
            p = self.gestor.crear_nueva_publicacion(f"{self.user_session}: {t}")
            p["imagen"] = self.temp_img_path
            p["comentarios"] = []
            self.temp_img_path = None
            self.guardar_todo()
            self.nodo_actual = self.gestor.lista_doble.cabeza
            self.mostrar_interfaz("global")

    def dar_like(self, pid):
        self.gestor.dar_like(pid)
        self.guardar_todo()
        self.mostrar_interfaz(self.current_view, self.target_user)


    def hacer_favorito(self, pid):
        if not pid: return
        mis_favs = self.favoritos.setdefault(self.user_session, [])
        if pid in mis_favs:
            mis_favs.remove(pid)
        else:
            mis_favs.append(pid)
        self.guardar_todo()
        self.mostrar_interfaz(self.current_view, self.target_user)

    def agregar_comentario(self, pid, ent_widget):
        texto = ent_widget.get().strip()
        if not texto or not pid: return
        todas_las_pubs = self.gestor.lista_simple.obtener_publicaciones()
        for p in todas_las_pubs:
            if p.get('id') == pid:
                if 'comentarios' not in p:
                    p['comentarios'] = []
                p['comentarios'].append(f"{self.user_session}: {texto}")
                break
        self.guardar_todo()
        self.mostrar_interfaz(self.current_view, self.target_user)


    def enviar_soli(self, destino):
        if destino not in self.usuarios: return
        self.solicitudes.setdefault(destino, {}).setdefault("recibidas", []).append(self.user_session)
        self.guardar_todo()
        messagebox.showinfo("Enviado", "Solicitud enviada.")

    def aceptar_soli(self, remitente):
        self.solicitudes[self.user_session]["recibidas"].remove(remitente)
        self.amigos.setdefault(self.user_session, []).append(remitente)
        self.amigos.setdefault(remitente, []).append(self.user_session)
        self.guardar_todo()
        self.mostrar_interfaz("solicitudes")

    def crear_card(self, p):
        card = tk.Frame(self.scroll_frame, bg=BG_CARD, pady=15, padx=20, highlightthickness=1,
                        highlightbackground=BORDER_COLOR)
        card.pack(fill="x", pady=10)

        user = p["contenido"].split(":")[0]
        msg = p["contenido"].split(":", 1)[1] if ":" in p["contenido"] else p["contenido"]

        tk.Label(card, text=f"@{user}", fg=TEXT_PRIMARY, bg=BG_CARD, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(card, text=msg, fg=TEXT_PRIMARY, bg=BG_CARD, wraplength=700, justify="left",
                 font=("Segoe UI", 11)).pack(anchor="w", pady=15)

        if p.get("imagen"):
            try:
                img = Image.open(p["imagen"]).resize((550, 300))
                itk = ImageTk.PhotoImage(img)
                li = tk.Label(card, image=itk, bg=BG_CARD)
                li.image = itk
                li.pack(pady=10)
            except:
                pass


        tk.Button(card, text=f"🖤 Me gusta ({p.get('likes', 0)})", bg=BG_CARD, fg="#ff4500",
                  font=("Segoe UI", 10, "bold"), bd=0, command=lambda: self.dar_like(p['id'])).pack(side="left")

        es_fav = p.get('id') in self.favoritos.get(self.user_session, [])
        texto_fav = "⭐ Quitar Favorito" if es_fav else "☆ Favorito"
        color_fav = "#f1c40f" if es_fav else TEXT_SECONDARY
        tk.Button(card, text=texto_fav, bg=BG_CARD, fg=color_fav, bd=0, font=("Segoe UI", 9, "bold"),
                  command=lambda: self.hacer_favorito(p.get('id'))).pack(side="right")


        frame_coms = tk.Frame(self.scroll_frame, bg="#1a2533", padx=15, pady=10)
        frame_coms.pack(fill="x", pady=(0, 15))

        tk.Label(frame_coms, text="Comentarios:", fg=TEXT_SECONDARY, bg="#1a2533", font=("Segoe UI", 8, "bold")).pack(
            anchor="w")

        for c in p.get("comentarios", []):
            tk.Label(frame_coms, text=c, fg=TEXT_PRIMARY, bg="#1a2533", font=("Segoe UI", 9), justify="left",
                     wraplength=700).pack(anchor="w")

        # Input de comentario
        f_input = tk.Frame(frame_coms, bg="#1a2533")
        f_input.pack(fill="x", pady=(5, 0))
        ent_com = tk.Entry(f_input, bg=BG_MAIN, fg="white", bd=0, font=("Segoe UI", 9))
        ent_com.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 10))
        self.crear_boton(f_input, "Comentar", lambda e=ent_com, pid=p.get('id'): self.agregar_comentario(pid, e),
                         bg="#1a1a1a", width=10).pack(side="right")
        # ---------------------------------------------------------------

    def crear_boton(self, parent, text, cmd, bg=ACCENT_PURPLE, width=None):
        b = tk.Button(parent, text=text, command=cmd, bg=bg, fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=15,
                      pady=8, cursor="hand2", width=width)
        b.bind("<Enter>", lambda e: b.config(bg=HOVER_PURPLE if bg == ACCENT_PURPLE or bg == "#0056b3" else "#333"))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b


if __name__ == "__main__":
    root = tk.Tk()
    app = EvilFaceBookApp(root)
    root.mainloop()