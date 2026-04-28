import os
import sys
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# ==================================================
# eFileCounter — Contador de archivos en tiempo real
# Diseñado para control de cajas en producción.
# ==================================================
# ================
# Versión: 2.5.0
# Build: Basilisk
# ================

# =============
# CÓMO FUNCIONA
# =============
# =====================================================================
#   - Lee una carpeta definida en CONFIG_FILE.
#   - Muestra cuántos archivos hay dentro, actualizándose cada segundo.
#   - Cambia de color cuando se alcanza el número objetivo por caja.
#   - Clic derecho → menú contextual con todas las opciones.
#   - Clic izquierdo + arrastrar → mover contador.
#   - El contador se pega automáticamente a los bordes de la pantalla.
#
#  MODO ÚNICOS (menú → "Contar únicos"):
#   Agrupa los archivos por el prefijo antes del "_" y cuenta cada
#   Datamatrix solo una vez, ignorando repeticiones.
# =====================================================================

# =============================
# INFORMACIÓN DE LA HERRAMIENTA
# =============================
APP_NAME        = "eFileCounter"
APP_VERSION     = "2.5.0 | Basilisk"
APP_AUTHOR      = "Created by Josu Manzanas"
APP_DESCRIPTION = (
    "Contador de archivos en tiempo real.\n"
    "Diseñado para control de cajas."
)

# ================
# RUTAS Y REGISTRO
# ================
# ===================================================================
# CONFIG_FILE: Archivo de configuración con la carpeta a monitorizar.
# Formato esperado: origin=C:\ruta\a\tu\carpeta
# ====================================================================
CONFIG_FILE          = r"C:\Path_Setup.txt"

# ===============================
# REGISTROS | INICIAR CON WINDOWS
# ===============================
RUN_REG_PATH         = r"Software\Microsoft\Windows\CurrentVersion\Run"
ZONE_MAP_POLICY      = r"Software\Policies\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap"
ZONE_MAP_DOMAINS     = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Domains"
ZONE_MAP_ESC_DOMAINS = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\EscDomains"

# ==============
# COMPORTAMIENTO
# ==============
INTERVAL_MS   = 1000   # Refresco del contador en milisegundos
SNAP_DISTANCE = 50     # Píxeles al borde para activar el snap


# =================================
# TAMAÑO SEGÚN DÍGITOS DEL CONTADOR
# =================================
# ========================================================================
# La ventana se redimensiona dinámicamente al cambiar de rango de dígitos.
# Clave = Número de dígitos del valor actual.
# ========================================================================
SIZE_BY_DIGITS = {
    1: {"width": 128, "height": 128, "font": 64},
    2: {"width": 128, "height": 128, "font": 64},
    3: {"width": 194, "height": 128, "font": 64},
    4: {"width": 224, "height": 128, "font": 64},
    5: {"width": 256, "height": 128, "font": 64},
}
MIN_SIZE = (128, 128)
MAX_SIZE = (256, 128)

# ====================
# COLORES DEL CONTADOR
# ====================
# =====================================================
#  - Neutro/Blanco: Sin objetivo o por debajo de él.
#  - SUCCESS_COLOR: Se alcanzó exactamente el objetivo.
#  - ERROR_COLOR: Se superó el objetivo o Error.
# =====================================================
SUCCESS_COLOR = "#00c853"
ERROR_COLOR   = "#d32f2f"

# =================
# MODO OSCURO/CLARO
# =================
THEMES = {
    "dark": {
        "bg":           "#0f0f0f",
        "fg":           "#ffffff",
        "menu_bg":      "#1c1c1c",
        "menu_hover":   "#2a2a2a",
        "menu_fg":      "#ffffff",
        "menu_sep":     "#333333",
        "entry_bg":     "#2b2b2b",
        "entry_border": "#555555",
        "btn_fg":       "#ffffff",
        "btn_bg":       "#3a3a3a",
        "btn_hover":    "#4a4a4a",
    },
    "light": {
        "bg":           "#f0f0f0",
        "fg":           "#000000",
        "menu_bg":      "#ffffff",
        "menu_hover":   "#e0e0e0",
        "menu_fg":      "#000000",
        "menu_sep":     "#cccccc",
        "entry_bg":     "#ffffff",
        "entry_border": "#aaaaaa",
        "btn_fg":       "#000000",
        "btn_bg":       "#e0e0e0",
        "btn_hover":    "#d0d0d0",
    },
}

def th():
    """Devuelve el diccionario de colores del tema activo."""
    return THEMES["dark" if dark_mode else "light"]

# =======
# IDIOMAS
# =======
# ===================================================
# Tres idiomas disponibles: español, inglés, euskera.
# t(key) devuelve el texto del idioma activo.
# ===================================================
DEFAULT_LANG = "es"
current_lang = DEFAULT_LANG

LANG = {
    "es": {
        "startup_title":          "Configuración inicial",
        "startup_question":       "¿Cuántos van en cada caja?",
        "target_title":           "Valor objetivo",
        "target_question":        "Cambiar número por caja:",
        "always_on_top":          "Siempre visible",
        "windows_bar":            "Barra de ventanas",
        "dark_mode":              "Modo oscuro",
        "start_with_windows":     "Iniciar con Windows",
        "target":                 "Objetivo",
        "unique_mode":            "Contar únicos",
        "about":                  "Acerca de",
        "close":                  "Cerrar",
        "language":               "Idioma",
        "startup_confirm_title":  "Inicio con Windows",
        "startup_confirm_enable": "¿Quieres activar el inicio automático?\n\nTambién se intentará configurar la ruta de red como Intranet local para reducir avisos.",
        "startup_confirm_disable":"¿Quieres desactivar el inicio automático?",
        "startup_ok_enable":      "Inicio automático activado.",
        "startup_ok_disable":     "Inicio automático desactivado.",
        "startup_error":          "No se pudo aplicar la configuración de inicio automático.",
        "startup_net_ok":         "Configuración de red aplicada para el servidor: {server}",
        "startup_net_error":      "No se pudo aplicar la configuración de red para el servidor: {server}",
        "version":                "Versión",
        "author":                 "Autor",
        "confirm":                "Confirmar",
        "cancel":                 "Cancelar",
        "lang_es":                "Español",
        "lang_en":                "English",
        "lang_eu":                "Euskera",
        "config_missing":         "Archivo de configuración no encontrado:\n{path}",
        "config_no_origin":       "No se encontró 'origin=' en el archivo de configuración.",
        "app_description":        "Contador de archivos en tiempo real.\nDiseñado para control de cajas.",
    },
    "en": {
        "startup_title":          "Initial setup",
        "startup_question":       "How many per box?",
        "target_title":           "Target value",
        "target_question":        "Change items per box:",
        "always_on_top":          "Always on Top",
        "windows_bar":            "Windows Bar",
        "dark_mode":              "Dark Mode",
        "start_with_windows":     "Start with Windows",
        "target":                 "Target",
        "unique_mode":            "Count unique",
        "about":                  "About",
        "close":                  "Close",
        "language":               "Language",
        "startup_confirm_title":  "Start with Windows",
        "startup_confirm_enable": "Do you want to enable auto-start?\n\nThe app will also try to trust the network path as Local Intranet to reduce warnings.",
        "startup_confirm_disable":"Do you want to disable auto-start?",
        "startup_ok_enable":      "Auto-start enabled.",
        "startup_ok_disable":     "Auto-start disabled.",
        "startup_error":          "Could not apply auto-start settings.",
        "startup_net_ok":         "Network trust configured for server: {server}",
        "startup_net_error":      "Could not configure network trust for server: {server}",
        "version":                "Version",
        "author":                 "Author",
        "confirm":                "Confirm",
        "cancel":                 "Cancel",
        "lang_es":                "Español",
        "lang_en":                "English",
        "lang_eu":                "Euskera",
        "config_missing":         "Configuration file not found:\n{path}",
        "config_no_origin":       "'origin=' not found in configuration file.",
        "app_description":        "Real-time file counter.\nDesigned for box control.",
    },
    "eu": {
        "startup_title":          "Hasierako konfigurazioa",
        "startup_question":       "Zenbat sartzen dira kutxa bakoitzean?",
        "target_title":           "Helburu-balioa",
        "target_question":        "Aldatu kutxa bakoitzeko kopurua:",
        "always_on_top":          "Beti ikusgai",
        "windows_bar":            "Leiho-barra",
        "dark_mode":              "Modu iluna",
        "start_with_windows":     "Windows-ekin hasi",
        "target":                 "Helburua",
        "unique_mode":            "Bakarrak zenbatu",
        "about":                  "Honi buruz",
        "close":                  "Itxi",
        "language":               "Hizkuntza",
        "startup_confirm_title":  "Windows-ekin hasi",
        "startup_confirm_enable": "Hasieran automatikoki abiaraztea aktibatu nahi duzu?\n\nGainera, sareko bidea Intranet lokal gisa konfiguratzen saiatuko da abisuak gutxitzeko.",
        "startup_confirm_disable":"Hasieran automatikoki abiaraztea desaktibatu nahi duzu?",
        "startup_ok_enable":      "Hasierako abiarazte automatikoa aktibatuta.",
        "startup_ok_disable":     "Hasierako abiarazte automatikoa desaktibatuta.",
        "startup_error":          "Ezin izan da hasierako konfigurazioa aplikatu.",
        "startup_net_ok":         "Sare-konfiantza konfiguratuta zerbitzariarentzat: {server}",
        "startup_net_error":      "Ezin izan da sare-konfiantza konfiguratu zerbitzariarentzat: {server}",
        "version":                "Bertsioa",
        "author":                 "Egilea",
        "confirm":                "Baieztatu",
        "cancel":                 "Utzi",
        "lang_es":                "Español",
        "lang_en":                "English",
        "lang_eu":                "Euskera",
        "config_missing":         "Konfigurazio-fitxategia ez da aurkitu:\n{path}",
        "config_no_origin":       "Ez da 'origin=' aurkitu konfigurazio-fitxategian.",
        "app_description":        "Denbora errealeko fitxategi-zenbagailua.\nKutxen kontrolerako diseinatua.",
    },
}

def t(key: str) -> str:
    """Devuelve el texto en el idioma activo. Si la clave no existe, devuelve la clave."""
    return LANG[current_lang].get(key, key) or key

# ==============
# ESTADO INTERNO
# ==============
# ================================================================================
# dark_mode        → True = tema oscuro, False = tema claro.
# titlebar_visible → True = barra de título de Windows visible.
# unique_mode      → True = cuenta Datamatrix únicos; False = todos los archivos.
# origin_folder    → carpeta monitorizada (leída del config).
# target_value     → objetivo por caja (introducido por el usuario).
# snap_x / snap_y  → borde detectado al soltar la ventana.
# _last_digits     → dígitos del último valor; evita redimensionar sin cambio.
# ================================================================================

dark_mode        = True
titlebar_visible = False
unique_mode      = True
origin_folder    = None
target_value     = None
snap_x           = None
snap_y           = None
_last_digits     = None

# =============
# CONFIGURACIÓN
# =============
def load_config():
    """Lee CONFIG_FILE y carga origin_folder. Avisa al usuario si hay problemas."""
    global origin_folder

    if not os.path.exists(CONFIG_FILE):
        msg = t("config_missing").format(path=CONFIG_FILE)
        window.after(400, lambda: messagebox.showwarning(APP_NAME, msg))
        return

    found = False
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.lower().startswith("origin="):
                    origin_folder = line.split("=", 1)[1].strip()
                    found = True
                    break
    except Exception:
        pass

    if not found:
        msg = t("config_no_origin")
        window.after(400, lambda: messagebox.showwarning(APP_NAME, msg))

# =============================
# INICIAR CON WINDOWS (AUTORUN)
# =============================
def get_startup_command():
    """Construye el comando que Windows ejecutará al inicio de sesión."""
    if getattr(sys, "frozen", False):
        return f'"{os.path.abspath(sys.executable)}"'

    python_exec = os.path.abspath(sys.executable)
    if python_exec.lower().endswith("python.exe"):
        pythonw = python_exec[:-10] + "pythonw.exe"
        if os.path.exists(pythonw):
            python_exec = pythonw

    script_path = os.path.abspath(sys.argv[0])
    return f'"{python_exec}" "{script_path}"'

def is_startup_enabled():
    """Devuelve True si existe la entrada de autorun en el registro."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_REG_PATH, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
        return bool(str(value).strip())
    except Exception:
        return False

def set_startup_enabled(enabled):
    """Activa o desactiva el arranque automático en el registro de Windows."""
    try:
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_REG_PATH) as key:
            if enabled:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, get_startup_command())
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
        return True
    except Exception:
        return False

def get_launch_target_path():
    """Ruta real del ejecutable o script que se lanza al inicio."""
    if getattr(sys, "frozen", False):
        return os.path.abspath(sys.executable)
    return os.path.abspath(sys.argv[0])

def extract_unc_server(path):
    """Extrae el nombre del servidor de una ruta UNC (\\\\Servidor\\...)."""
    if not path:
        return None
    p = path.strip().strip('"')
    if not p.startswith("\\\\"):
        return None
    parts = p[2:].split("\\", 1)
    if not parts or not parts[0]:
        return None
    return parts[0]

def configure_unc_as_intranet(server):
    """Marca un servidor UNC como Intranet local para el usuario actual."""
    if not server:
        return False
    try:
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, ZONE_MAP_POLICY) as key:
            winreg.SetValueEx(key, "UNCAsIntranet", 0, winreg.REG_DWORD, 1)
        for base in (ZONE_MAP_DOMAINS, ZONE_MAP_ESC_DOMAINS):
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{base}\\{server}") as key:
                winreg.SetValueEx(key, "file", 0, winreg.REG_DWORD, 1)
        return True
    except Exception:
        return False

# ================
# LÓGICA DE CONTEO
# ================
def get_datamatrix_prefix(filename):
    """Extrae el prefijo Datamatrix de un nombre de archivo.
    Todo lo que hay antes del primer "_" (sin extensión).
    Ej: "123456-0014-005_84584.xml"  →  "123456-0014-005"
    """
    name = os.path.splitext(filename)[0]
    return name.split("_", 1)[0].strip()

def count_all_files(folder):
    """Cuenta TODOS los archivos de la carpeta sin distinción.
    Devuelve 0 si la carpeta no existe o hay un error de acceso."""
    if not folder or not os.path.exists(folder):
        return 0
    try:
        return sum(1 for e in os.scandir(folder) if e.is_file())
    except Exception:
        return 0

def count_unique_datamatrix(folder):
    """Cuenta los Datamatrix únicos en la carpeta (solo archivos .xml).
    De cada grupo con el mismo prefijo se queda con el más reciente."""
    if not folder or not os.path.exists(folder):
        return 0
    try:
        latest = {}
        for entry in os.scandir(folder):
            if not entry.is_file():
                continue
            if not entry.name.lower().endswith(".xml"):
                continue
            prefix = get_datamatrix_prefix(entry.name)
            ctime  = entry.stat().st_mtime
            if prefix not in latest or ctime > latest[prefix]:
                latest[prefix] = ctime
        return len(latest)
    except Exception:
        return 0

# =================
# SNAP A LOS BORDES
# =================
def detect_snap_edges():
    """Detecta a qué bordes de pantalla está cerca la ventana
    y actualiza snap_x / snap_y."""
    global snap_x, snap_y

    wx, wy = window.winfo_x(), window.winfo_y()
    ww, wh = window.winfo_width(), window.winfo_height()
    sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()

    snap_x = None
    if   abs(wx) < SNAP_DISTANCE:             snap_x = "left"
    elif abs((wx + ww) - sw) < SNAP_DISTANCE: snap_x = "right"

    snap_y = None
    if   abs(wy) < SNAP_DISTANCE:             snap_y = "top"
    elif abs((wy + wh) - sh) < SNAP_DISTANCE: snap_y = "bottom"

def apply_snap_edges():
    """Mueve la ventana exactamente al borde detectado por detect_snap_edges()."""
    x, y   = window.winfo_x(), window.winfo_y()
    w, h   = window.winfo_width(), window.winfo_height()
    sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()

    if   snap_x == "left":   x = 0
    elif snap_x == "right":  x = sw - w
    if   snap_y == "top":    y = 0
    elif snap_y == "bottom": y = sh - h

    window.geometry(f"+{x}+{y}")

# ========
# INTERFAZ
# ========
def apply_window_size_for(value):
    """Redimensiona la ventana y ajusta la fuente según el número de dígitos.
    Después reaplica el snap para que la ventana siga pegada al borde."""
    detect_snap_edges()
    preset = SIZE_BY_DIGITS.get(min(len(str(value)), 5), SIZE_BY_DIGITS[1])

    window.geometry(f"{preset['width']}x{preset['height']}")
    label.configure(font=ctk.CTkFont(family="Segoe UI", size=preset["font"], weight="bold"))
    window.update_idletasks()
    apply_snap_edges()

def apply_theme():
    """Aplica el tema visual (oscuro/claro) a la ventana principal."""
    ctk.set_appearance_mode("dark" if dark_mode else "light")
    window.configure(fg_color=th()["bg"])

def update_counter():
    """Bucle principal. Se ejecuta cada INTERVAL_MS ms.
    Actualiza el label cada tick; solo redimensiona si cambia el rango de dígitos."""

    # Carpeta no configurada o inaccesible → mostrar ERR
    if not origin_folder or not os.path.exists(origin_folder):
        label.configure(text="ERR", text_color=ERROR_COLOR)
        window.after(INTERVAL_MS, update_counter)
        return

    # Conteo según modo activo
    value = count_unique_datamatrix(origin_folder) if unique_mode else count_all_files(origin_folder)

    # Color según relación con el objetivo
    if target_value is None or value < target_value:
        text_color = th()["fg"]
    elif value == target_value:
        text_color = SUCCESS_COLOR
    else:
        text_color = ERROR_COLOR

    # Actualizar label
    label.configure(text=str(value), text_color=text_color)

    # Redimensionar solo si el número de dígitos ha cambiado (ej: 99 → 100)
    global _last_digits
    current_digits = len(str(value))
    if current_digits != _last_digits:
        apply_window_size_for(value)
        _last_digits = current_digits

    window.after(INTERVAL_MS, update_counter)

# =====================
# UTILIDADES DE VENTANA
# =====================
def _center_on_screen(win):
    """Centra una ventana CTkToplevel en la pantalla."""
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    w  = win.winfo_width()
    h  = win.winfo_height()
    win.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

def _center_on_parent(win, parent):
    """Centra una ventana CTkToplevel respecto a su ventana padre."""
    win.update_idletasks()
    w,  h  = win.winfo_width(),    win.winfo_height()
    px, py = parent.winfo_rootx(), parent.winfo_rooty()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    x = max(0, px + (pw - w) // 2)
    y = max(0, py + (ph - h) // 2)
    win.geometry(f"+{x}+{y}")

# ===========================
# DIÁLOGO DE ENTRADA NUMÉRICA
# ===========================
def show_input_dialog(title, question, callback):
    """Abre un diálogo modal para introducir un número entero >= 1.
    Llama a callback(valor) al confirmar."""
    was_topmost = window.attributes("-topmost")
    window.attributes("-topmost", False)

    dialog = ctk.CTkToplevel(window)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.attributes("-topmost", True)
    dialog.grab_set()

    ctk.CTkLabel(
        dialog,
        text = title,
        font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
    ).pack(padx=30, pady=(25, 4))

    ctk.CTkLabel(
        dialog,
        text       = question,
        font       = ctk.CTkFont(family="Segoe UI", size=12),
        text_color = "gray70" if dark_mode else "gray40",
    ).pack(padx=30, pady=(0, 12))

    entry = ctk.CTkEntry(
        dialog,
        width   = 120,
        height  = 36,
        justify = "center",
        font    = ctk.CTkFont(family="Segoe UI", size=16),
    )
    entry.pack(padx=30, pady=(0, 16))

    def _focus_entry():
        dialog.lift()
        dialog.focus_force()
        entry.focus_force()

    dialog.after(150, _focus_entry)

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(padx=30, pady=(0, 20))

    def on_confirm():
        try:
            val = int(entry.get())
            if val >= 1:
                window.attributes("-topmost", was_topmost)
                dialog.destroy()
                callback(val)
        except ValueError:
            entry.configure(border_color=ERROR_COLOR)

    def on_cancel():
        window.attributes("-topmost", was_topmost)
        dialog.destroy()

    ctk.CTkButton(
        btn_frame,
        text    = t("confirm"),
        command = on_confirm,
        width   = 90,
        height  = 32,
    ).pack(side="left", padx=(0, 8))

    ctk.CTkButton(
        btn_frame,
        text        = t("cancel"),
        command     = on_cancel,
        width       = 90,
        height      = 32,
        fg_color    = th()["btn_bg"],
        hover_color = th()["btn_hover"],
        text_color  = th()["btn_fg"],
    ).pack(side="left")

    dialog.bind("<Return>", lambda e: on_confirm())
    dialog.bind("<Escape>", lambda e: on_cancel())

    _center_on_screen(dialog)

# =========
# ACERCA DE
# =========
def show_about():
    """Abre la ventana informativa Acerca de"""
    about = ctk.CTkToplevel(window)
    about.title(t("about"))
    about.resizable(False, False)
    about.attributes("-topmost", True)

    ctk.CTkLabel(
        about,
        text = APP_NAME,
        font = ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
    ).pack(padx=40, pady=(28, 2))

    ctk.CTkLabel(
        about,
        text       = f"v{APP_VERSION}",
        font       = ctk.CTkFont(family="Segoe UI", size=11),
        text_color = "gray60" if dark_mode else "gray40",
    ).pack(padx=40, pady=(0, 14))

    ctk.CTkFrame(about, height=1, fg_color=th()["menu_sep"]).pack(fill="x", padx=30)

    ctk.CTkLabel(
        about,
        text    = t("app_description"),
        justify = "center",
        font    = ctk.CTkFont(family="Segoe UI", size=12),
    ).pack(padx=40, pady=16)

    ctk.CTkFrame(about, height=1, fg_color=th()["menu_sep"]).pack(fill="x", padx=30)

    ctk.CTkLabel(
        about,
        text       = APP_AUTHOR,
        font       = ctk.CTkFont(family="Segoe UI", size=11),
        text_color = "gray60" if dark_mode else "gray40",
    ).pack(padx=40, pady=(14, 0))

    ctk.CTkButton(
        about,
        text    = t("close"),
        command = about.destroy,
        width   = 110,
        height  = 34,
    ).pack(pady=20)

    _center_on_screen(about)

# ===============
# MENÚ CONTEXTUAL
# ===============
_ctx_menu_window = None

def close_context_menu():
    """Cierra el panel de menú flotante si está abierto."""
    global _ctx_menu_window
    if _ctx_menu_window and _ctx_menu_window.winfo_exists():
        _ctx_menu_window.destroy()
    _ctx_menu_window = None

def show_context_menu(event):
    """Construye y muestra el menú contextual CTk en la posición del cursor."""
    global _ctx_menu_window

    close_context_menu()

    theme          = th()
    MENU_PAD_X     = 3
    MENU_PAD_LEFT  = 8
    MENU_FONT_SIZE = 11

    # --- Estructura del panel ---
    panel = ctk.CTkToplevel(window)
    panel.overrideredirect(True)
    panel.attributes("-topmost", True)
    panel.configure(fg_color=theme["menu_bg"])

    outer = ctk.CTkFrame(panel, fg_color=theme["menu_sep"], corner_radius=6)
    outer.pack(padx=1, pady=1, fill="both", expand=True)

    inner = ctk.CTkFrame(outer, fg_color=theme["menu_bg"], corner_radius=5)
    inner.pack(padx=1, pady=1, fill="both", expand=True)

    _ctx_menu_window = panel
    menu_vars = []

    # --- Constructores de elementos del menú ---

    def add_option(text, command, bold=False):
        def on_click():
            close_context_menu()
            command()

        ctk.CTkButton(
            inner,
            text           = text,
            command        = on_click,
            anchor         = "w",
            width          = 180,
            height         = 24,
            corner_radius  = 4,
            fg_color       = "transparent",
            hover_color    = theme["menu_hover"],
            text_color     = theme["menu_fg"],
            font           = ctk.CTkFont(family="Segoe UI", size=MENU_FONT_SIZE,
                                         weight="bold" if bold else "normal"),
            border_spacing = MENU_PAD_LEFT,
        ).pack(fill="x", padx=MENU_PAD_X, pady=0)

    def add_checkbox_option(text, checked, command):
        var = tk.BooleanVar(value=checked)
        menu_vars.append(var)

        border_normal = "#c8c8c8" if dark_mode else "#4a4a4a"
        border_hover  = "#ededed" if dark_mode else "#2f2f2f"

        def on_toggle():
            close_context_menu()
            command()

        row = ctk.CTkFrame(inner, fg_color="transparent", corner_radius=4)
        row.pack(fill="x", padx=MENU_PAD_X, pady=0)

        lbl = ctk.CTkLabel(
            row,
            text       = text,
            text_color = theme["menu_fg"],
            font       = ctk.CTkFont(family="Segoe UI", size=MENU_FONT_SIZE),
            anchor     = "w",
        )
        lbl.pack(side="left", fill="x", expand=True, padx=(MENU_PAD_LEFT, 4), pady=3)

        chk = ctk.CTkCheckBox(
            row,
            text            = "",
            variable        = var,
            onvalue         = True,
            offvalue        = False,
            command         = on_toggle,
            width           = 16,
            height          = 16,
            checkbox_width  = 13,
            checkbox_height = 13,
            border_width    = 1,
            corner_radius   = 3,
            fg_color        = theme["menu_fg"],
            hover_color     = theme["menu_hover"],
            border_color    = border_normal,
            checkmark_color = theme["menu_bg"],
        )
        chk.pack(side="right", padx=(0, 4), pady=3)

        def _on_enter(_e):
            row.configure(fg_color=theme["menu_hover"])
            chk.configure(border_color=border_hover)

        def _on_leave(_e):
            px, py = row.winfo_pointerxy()
            rx, ry = row.winfo_rootx(), row.winfo_rooty()
            rw, rh = row.winfo_width(), row.winfo_height()
            if not (rx <= px < rx + rw and ry <= py < ry + rh):
                row.configure(fg_color="transparent")
                chk.configure(border_color=border_normal)

        def _bind_hover(w):
            w.bind("<Enter>", _on_enter)
            w.bind("<Leave>", _on_leave)

        for w in (row, lbl):
            w.bind("<Button-1>", lambda _e: on_toggle())
            _bind_hover(w)

        _bind_hover(chk)
        for child in chk.winfo_children():
            _bind_hover(child)

    def add_separator(pady=2):
        ctk.CTkFrame(inner, height=1, fg_color=theme["menu_sep"]).pack(
            fill="x", padx=MENU_PAD_X, pady=pady
        )

    def add_mid_separator():
        color = "#444444" if dark_mode else theme["menu_sep"]
        ctk.CTkFrame(inner, height=1, fg_color=color).pack(
            fill="x", padx=MENU_PAD_X, pady=1
        )

    def add_language_option():
        def open_lang_popup():
            close_context_menu()

            popup = ctk.CTkToplevel(window)
            popup.title(t("language"))
            popup.resizable(False, False)
            popup.attributes("-topmost", True)
            popup.grab_set()
            popup.configure(fg_color="#1d1d1d" if dark_mode else th()["bg"])

            if dark_mode:
                c_title  = "#f3f3f3"
                c_sub    = "#c9c9c9"
                c_btn    = "#3a3a3a"
                c_hover  = "#474747"
                c_active = "#1f6fb3"
                c_ahover = "#2b82cc"
                c_atext  = "#f2f2f2"
            else:
                c_title  = "#1f1f1f"
                c_sub    = "#555555"
                c_btn    = "#ececec"
                c_hover  = "#e0e0e0"
                c_active = "#2f7fbd"
                c_ahover = "#276a9d"
                c_atext  = "#f7f7f7"

            ctk.CTkLabel(
                popup,
                text       = t("language"),
                font       = ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
                text_color = c_title,
            ).pack(padx=40, pady=(26, 12))

            ctk.CTkLabel(
                popup,
                text       = "Selecciona idioma:",
                font       = ctk.CTkFont(family="Segoe UI", size=12),
                text_color = c_sub,
            ).pack(padx=40, pady=(0, 12))

            btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
            btn_frame.pack(padx=40, pady=(0, 8), fill="x")

            def pick_lang(lang):
                set_language(lang)
                popup.destroy()

            for code, label_text in [("es", t("lang_es")), ("en", t("lang_en")), ("eu", t("lang_eu"))]:
                active = (code == current_lang)
                ctk.CTkButton(
                    btn_frame,
                    text        = label_text,
                    command     = lambda c=code: pick_lang(c),
                    width       = 170,
                    height      = 34,
                    fg_color    = c_active if active else c_btn,
                    hover_color = c_ahover if active else c_hover,
                    text_color  = c_atext  if active else c_title,
                    font        = ctk.CTkFont(family="Segoe UI", size=12,
                                              weight="bold" if active else "normal"),
                ).pack(fill="x", pady=4)

            ctk.CTkButton(
                popup,
                text        = t("close"),
                command     = popup.destroy,
                width       = 170,
                height      = 34,
                fg_color    = c_btn,
                hover_color = c_hover,
                text_color  = c_title,
            ).pack(pady=(10, 22))

            popup.bind("<Escape>", lambda e: popup.destroy())
            _center_on_screen(popup)

        add_option(t("language"), open_lang_popup)

    # --- Construir entradas del menú ---
    ctk.CTkFrame(inner, height=3, fg_color="transparent").pack()

    add_separator()
    add_checkbox_option(t("always_on_top"),     bool(window.attributes("-topmost")), toggle_topmost)
    add_separator(pady=0)
    add_checkbox_option(t("windows_bar"),        titlebar_visible,     toggle_titlebar)
    add_separator(pady=0)
    add_checkbox_option(t("dark_mode"),          dark_mode,            toggle_dark_mode)
    add_separator(pady=0)
    add_checkbox_option(t("unique_mode"),        unique_mode,          toggle_unique_mode)
    add_separator(pady=0)
    add_checkbox_option(t("start_with_windows"), is_startup_enabled(), toggle_startup_with_windows)
    add_option(f"{t('target')}: {target_value if target_value else 'None'}", set_target_value)
    add_mid_separator()
    add_language_option()
    add_option(t("about"), show_about)
    add_option(t("close"), close_app, bold=True)

    ctk.CTkFrame(inner, height=3, fg_color="transparent").pack()

    # Posicionar el panel junto al cursor, ajustando si se sale de pantalla
    panel.update_idletasks()
    px, py = event.x_root, event.y_root
    pw, ph = panel.winfo_width(), panel.winfo_height()
    sw, sh = panel.winfo_screenwidth(), panel.winfo_screenheight()
    if px + pw > sw: px -= pw
    if py + ph > sh: py -= ph
    panel.geometry(f"+{px}+{py}")

    # Cerrar el menú al perder el foco o al hacer clic en la ventana principal
    panel.bind("<FocusOut>", lambda e: close_context_menu())
    panel.focus_set()

    def _close_on_main_click(e):
        close_context_menu()

    window.bind("<Button-1>", _close_on_main_click, add="+")
    label.bind("<Button-1>",  _close_on_main_click, add="+")

# =================
# ACCIONES DEL MENÚ
# =================
def toggle_topmost():
    """Alterna el modo 'siempre visible'."""
    window.attributes("-topmost", not window.attributes("-topmost"))

def toggle_titlebar():
    """Muestra u oculta la barra de título de Windows.
    Al mostrarla, reaplica el topmost para no perder el foco."""
    global titlebar_visible
    titlebar_visible = not titlebar_visible
    window.overrideredirect(not titlebar_visible)
    if titlebar_visible:
        current_topmost = window.attributes("-topmost")
        window.after(50, lambda: window.attributes("-topmost", current_topmost))

def toggle_dark_mode():
    """Alterna entre tema oscuro y claro."""
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()

def toggle_unique_mode():
    """Alterna el modo de conteo (en memoria, no persiste)."""
    global unique_mode
    unique_mode = not unique_mode

def toggle_startup_with_windows():
    """Alterna el inicio automático con confirmación y configuración de red."""
    currently_enabled = is_startup_enabled()
    enable = not currently_enabled

    question = t("startup_confirm_enable") if enable else t("startup_confirm_disable")
    if not messagebox.askyesno(t("startup_confirm_title"), question, parent=window):
        return

    launch_path = get_launch_target_path()
    unc_server  = extract_unc_server(launch_path)
    if enable and unc_server:
        if configure_unc_as_intranet(unc_server):
            msg_net = t("startup_net_ok").format(server=unc_server)
            messagebox.showinfo(t("startup_confirm_title"), msg_net, parent=window)
        else:
            msg_net = t("startup_net_error").format(server=unc_server)
            messagebox.showwarning(t("startup_confirm_title"), msg_net, parent=window)

    if set_startup_enabled(enable):
        messagebox.showinfo(
            t("startup_confirm_title"),
            t("startup_ok_enable") if enable else t("startup_ok_disable"),
            parent=window,
        )
    else:
        messagebox.showerror(t("startup_confirm_title"), t("startup_error"), parent=window)

def set_language(lang):
    """Cambia el idioma activo de la interfaz."""
    global current_lang
    current_lang = lang

def ask_target_on_startup():
    """Muestra el diálogo de configuración inicial al arrancar."""
    show_input_dialog(t("startup_title"), t("startup_question"), _apply_target)

def set_target_value():
    """Abre el diálogo para cambiar el objetivo desde el menú."""
    show_input_dialog(t("target_title"), t("target_question"), _apply_target)

def _apply_target(value):
    """Guarda el nuevo valor objetivo."""
    global target_value
    target_value = value

def close_app():
    """Cierra la aplicación."""
    window.destroy()

# ===============
# ARRASTRAR/MOVER
# ===============
drag_offset = {"x": 0, "y": 0}

def start_drag(event):
    drag_offset["x"] = event.x
    drag_offset["y"] = event.y

def on_drag(event):
    nx = window.winfo_pointerx() - drag_offset["x"]
    ny = window.winfo_pointery() - drag_offset["y"]
    window.geometry(f"+{nx}+{ny}")

def on_release(event):
    detect_snap_edges()
    apply_snap_edges()

# =====================
# CONSTRUCCIÓN CONTADOR
# =====================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

window = ctk.CTk()
window.title(APP_NAME)
window.geometry("128x128")
window.minsize(*MIN_SIZE)
window.maxsize(*MAX_SIZE)
window.attributes("-topmost", True)
window.overrideredirect(True)

label = ctk.CTkLabel(
    window,
    text       = "0",
    font       = ctk.CTkFont(family="Segoe UI", size=60, weight="bold"),
    fg_color   = "transparent",
    text_color = THEMES["dark"]["fg"],
)
label.place(relx=0.5, rely=0.5, anchor="center")

for widget in (window, label):
    widget.bind("<Button-3>",        show_context_menu)
    widget.bind("<Button-1>",        start_drag)
    widget.bind("<B1-Motion>",       on_drag)
    widget.bind("<ButtonRelease-1>", on_release)

# ========
# ARRANQUE
# ========
load_config()
apply_theme()

# Posicionar en la esquina superior derecha al arrancar
window.after(0, lambda: window.geometry(
    f"+{window.winfo_screenwidth() - window.winfo_width()}+0"
))

# Mostrar diálogo de objetivo con pequeño retardo para que la ventana esté lista
window.after(5, ask_target_on_startup)

update_counter()
window.mainloop()

# ========================
# Created by Josu Manzanas
# ========================