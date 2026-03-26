import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import os
from datetime import datetime

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

        self.user_session = None
        self.temp_img_path = None
        self.current_view = "global"
        self.target_user = None

        self.pantalla_login()

    def guardar_todo(self):
        with open("usuarios.json", "w") as f: json.dump(self.usuarios, f)
        with open("amigos.json", "w") as f: json.dump(self.amigos, f)
        with open("solicitudes.json", "w") as f: json.dump(self.solicitudes, f)
        self.gestor.guardar_datos()

    # ---LOGIN ---
    def pantalla_login(self):
        for w in self.root.winfo_children(): w.destroy()
        f = tk.Frame(self.root, bg=BG_MAIN)
        f.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(f, text="EVIL FACEBOOK", fg=TEXT_PRIMARY, bg=BG_MAIN, font=("Segoe UI", 45, "bold")).pack()

        # Campo de Usuario
        self.ent_user = tk.Entry(f, bg=BG_CARD, fg="white", insertbackground="white", font=("Segoe UI", 12), bd=0,
                                 justify="center")
        self.ent_user.pack(ipady=10, ipadx=30, pady=(20, 10))
        self.ent_user.insert(0, "aki")

        # Campo de Contraseña
        self.ent_pass = tk.Entry(f, bg=BG_CARD, fg="white", insertbackground="white", font=("Segoe UI", 12), bd=0,
                                 justify="center", show="*")  # El show="*" oculta los caracteres
        self.ent_pass.pack(ipady=10, ipadx=30, pady=(0, 20))
        self.ent_pass.insert(0, "1234")

        self.crear_boton(f, "ENTRAR", self.intentar_login, width=25).pack(pady=5)
        self.crear_boton(f, "REGISTRAR", self.registrar_usuario, bg="#1a1a1a", width=25).pack()

    def intentar_login(self):
        u = self.ent_user.get().lower().strip()
        p = self.ent_pass.get().strip()

        # Verifica si el usuario existe y si la contraseña coincide
        if u in self.usuarios and self.usuarios[u] == p:
            self.user_session = u
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
            self.usuarios[u] = p  # Guarda el usuario con su contraseña
            self.guardar_todo()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
        else:
            messagebox.showwarning("!", "El usuario ya existe.")

    # ---MAIN---
    def mostrar_interfaz(self, vista, usuario=None):
        pos_scroll = self.canvas.yview()[0] if hasattr(self, 'canvas') and self.canvas.winfo_exists() else 0

        for w in self.root.winfo_children(): w.destroy()
        self.current_view = vista
        self.target_user = usuario

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
        self.crear_boton(s_card, "FEED GLOBAL", lambda: self.mostrar_interfaz("global")).pack(fill="x", pady=(10, 5))
        self.crear_boton(s_card, "MI PERFIL", lambda: self.mostrar_interfaz("perfil", self.user_session)).pack(fill="x",
                                                                                                               pady=5)
        self.crear_boton(s_card, "AMIGOS", lambda: self.mostrar_interfaz("amigos")).pack(fill="x", pady=5)
        self.crear_boton(s_card, "SOLICITUDES", lambda: self.mostrar_interfaz("solicitudes")).pack(fill="x", pady=5)

        # Buscador
        tk.Label(sidebar, text="BUSCAR USUARIO", fg=TEXT_SECONDARY, bg=BG_MAIN, font=("Segoe UI", 7, "bold")).pack(
            pady=(20, 5), anchor="w")
        ent_bus = tk.Entry(sidebar, bg=BG_CARD, fg="white", bd=0)
        ent_bus.pack(fill="x", ipady=8)
        self.crear_boton(sidebar, "IR AL PERFIL", lambda: self.mostrar_interfaz("perfil", ent_bus.get().lower())).pack(
            pady=5, fill="x")

        # Área de Feed
        self.area_feed = tk.Frame(main_body, bg=BG_MAIN)
        self.area_feed.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(self.area_feed, bg=BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.area_feed, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=BG_MAIN)

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=600)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if vista == "global":
            self.render_feed()
        elif vista == "perfil":
            self.render_perfil(usuario)
        elif vista == "amigos":
            self.render_amigos()
        elif vista == "solicitudes":
            self.render_solicitudes()

        self.root.update_idletasks()
        if vista == "global": self.canvas.yview_moveto(pos_scroll)

    # --RENDERS--
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

        pubs = self.gestor.lista_simple.obtener_publicaciones()
        for p in pubs[::-1]: self.crear_card(p)

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

    # --Logica Posts--
    def subir_foto(self):
        self.temp_img_path = filedialog.askopenfilename()
        if self.temp_img_path: self.btn_img.config(text="✔ LISTA")

    def postear(self):
        t = self.ent_post.get()
        if t:
            p = self.gestor.crear_nueva_publicacion(f"{self.user_session}: {t}")
            p["imagen"] = self.temp_img_path
            self.temp_img_path = None
            self.guardar_todo()
            self.mostrar_interfaz("global")

    def dar_like(self, pid):
        self.gestor.dar_like(pid)
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
        card.pack(fill="x", pady=5)

        user = p["contenido"].split(":")[0]
        msg = p["contenido"].split(":", 1)[1] if ":" in p["contenido"] else p["contenido"]

        tk.Label(card, text=f"@{user}", fg=TEXT_PRIMARY, bg=BG_CARD, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(card, text=msg, fg=TEXT_PRIMARY, bg=BG_CARD, wraplength=550, justify="left").pack(anchor="w", pady=10)

        if p.get("imagen"):
            try:
                img = Image.open(p["imagen"]).resize((450, 250))
                itk = ImageTk.PhotoImage(img)
                li = tk.Label(card, image=itk, bg=BG_CARD)
                li.image = itk
                li.pack()
            except:
                pass

        tk.Button(card, text=f"🖤 {p['likes']}", bg=BG_CARD, fg="#ff4500", bd=0,
                  command=lambda: self.dar_like(p['id'])).pack(side="left")

    def crear_boton(self, parent, text, cmd, bg=ACCENT_PURPLE, width=None):
        b = tk.Button(parent, text=text, command=cmd, bg=bg, fg="white", font=("Segoe UI", 8, "bold"), bd=0, padx=15,
                      pady=8, cursor="hand2", width=width)
        b.bind("<Enter>", lambda e: b.config(bg=HOVER_PURPLE if bg == ACCENT_PURPLE else "#333"))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b


if __name__ == "__main__":
    root = tk.Tk()
    app = EvilFaceBookApp(root)
    root.mainloop()