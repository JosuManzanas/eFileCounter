import os
import sys
import tkinter as tk
from tkinter import messagebox

# En Python 3.4, winreg es estándar
try:
    import winreg
except ImportError:
    pass # Fallback por seguridad

# ==================================================
# eFileCounter — Contador de archivos en tiempo real
# Diseñado para control de cajas en producción.
# ==================================================
# ===============================================
# Versión: 2.5.0
# Build: Pangolin (Backport para sistemas legacy)
# Nota: Basada en la build Basilisk
# ===============================================

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

APP_NAME        = "eFileCounter"
APP_VERSION     = "2.5.0 | Pangolin"
APP_AUTHOR      = "Created by Josu Manzanas"
APP_DESCRIPTION = (
    "Contador de archivos en tiempo real.\n"
    "Diseñado para control de cajas."
)

CONFIG_FILE          = r"C:\Path_Setup.txt"
RUN_REG_PATH         = r"Software\Microsoft\Windows\CurrentVersion\Run"
ZONE_MAP_POLICY      = r"Software\Policies\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap"
ZONE_MAP_DOMAINS     = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Domains"
ZONE_MAP_ESC_DOMAINS = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\EscDomains"

INTERVAL_MS   = 1000
SNAP_DISTANCE = 50

SIZE_BY_DIGITS = {
    1: {"width": 128, "height": 128, "font": 64},
    2: {"width": 128, "height": 128, "font": 64},
    3: {"width": 194, "height": 128, "font": 64},
    4: {"width": 224, "height": 128, "font": 64},
    5: {"width": 256, "height": 128, "font": 64},
}
MIN_SIZE = (128, 128)
MAX_SIZE = (256, 128)

SUCCESS_COLOR = "#00c853"
ERROR_COLOR   = "#d32f2f"

THEMES = {
    "dark": {
        "bg":           "#0f0f0f",
        "fg":           "#ffffff",
        "menu_bg":      "#1c1c1c",
        "menu_hover":   "#2a2a2a",
        "menu_fg":      "#ffffff",
        "btn_bg":       "#3a3a3a",
        "btn_fg":       "#ffffff",
    },
    "light": {
        "bg":           "#f0f0f0",
        "fg":           "#000000",
        "menu_bg":      "#ffffff",
        "menu_hover":   "#e0e0e0",
        "menu_fg":      "#000000",
        "btn_bg":       "#e0e0e0",
        "btn_fg":       "#000000",
    },
}

def th():
    return THEMES["dark" if dark_mode else "light"]

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
        "startup_error":          "No se pudo aplicar la configuración.",
        "startup_net_ok":         "Configuración de red aplicada para: {server}",
        "startup_net_error":      "No se pudo configurar la red para: {server}",
        "lang_es":                "Español",
        "lang_en":                "English",
        "lang_eu":                "Euskera",
        "config_missing":         "Archivo de configuración no encontrado:\n{path}",
        "config_no_origin":       "No se encontró 'origin=' en la configuración.",
        "confirm":                "Confirmar",
        "cancel":                 "Cancelar",
        "app_description":        "Contador en tiempo real. Control de cajas.",
    },
    # Resto de idiomas omitidos por brevedad pero estructura igual,
    # solo asegúrate de no usar type hints
    "en": {"target": "Target", "startup_title": "Initial setup", "startup_question": "How many per box?", "close": "Close", "confirm": "Confirm", "cancel": "Cancel", "language": "Language", "always_on_top": "Always on Top", "windows_bar": "Windows Bar", "dark_mode": "Dark Mode", "unique_mode": "Count unique", "start_with_windows": "Start with Windows", "about": "About", "config_missing": "Missing: {path}", "config_no_origin": "Missing origin=", "startup_confirm_enable": "Enable auto-start?", "startup_confirm_disable": "Disable auto-start?", "startup_confirm_title": "Startup", "startup_ok_enable": "Enabled", "startup_ok_disable": "Disabled", "startup_error": "Error", "startup_net_ok": "Net OK {server}", "startup_net_error": "Net Error {server}", "lang_es": "Español", "lang_en": "English", "lang_eu": "Euskera", "target_title": "Target", "target_question": "New target:"},
    "eu": {"target": "Helburua", "startup_title": "Hasiera", "startup_question": "Zenbat kutxako?", "close": "Itxi", "confirm": "Bai", "cancel": "Ez", "language": "Hizkuntza", "always_on_top": "Beti ikusgai", "windows_bar": "Leiho-barra", "dark_mode": "Modu iluna", "unique_mode": "Bakarrak zenbatu", "start_with_windows": "Windows-ekin hasi", "about": "Honi buruz", "config_missing": "Ez da aurkitu: {path}", "config_no_origin": "origin= falta da", "startup_confirm_enable": "Hasiera automatikoa?", "startup_confirm_disable": "Kendu hasiera automatikoa?", "startup_confirm_title": "Hasiera", "startup_ok_enable": "Aktibatuta", "startup_ok_disable": "Desaktibatuta", "startup_error": "Errorea", "startup_net_ok": "Sarea ondo {server}", "startup_net_error": "Sare errorea {server}", "lang_es": "Español", "lang_en": "English", "lang_eu": "Euskera", "target_title": "Helburua", "target_question": "Helburu berria:"}
}

def t(key):
    return LANG.get(current_lang, LANG["es"]).get(key, key)

dark_mode        = True
titlebar_visible = False
unique_mode      = True
origin_folder    = None
target_value     = None
snap_x           = None
snap_y           = None
_last_digits     = None

def load_config():
    global origin_folder
    if not os.path.exists(CONFIG_FILE):
        msg = t("config_missing").format(path=CONFIG_FILE)
        window.after(400, lambda: messagebox.showwarning(APP_NAME, msg))
        return

    found = False
    try:
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line.lower().startswith("origin="):
                    origin_folder = line.split("=", 1)[1].strip()
                    found = True
                    break
    except Exception:
        pass

    if not found:
        window.after(400, lambda: messagebox.showwarning(APP_NAME, t("config_no_origin")))

def get_startup_command():
    if getattr(sys, "frozen", False):
        return '"{}"'.format(os.path.abspath(sys.executable))
    script_path = os.path.abspath(sys.argv[0])
    return '"{}" "{}"'.format(sys.executable, script_path)

def is_startup_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_REG_PATH, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
        return bool(str(value).strip())
    except Exception:
        return False

def set_startup_enabled(enabled):
    try:
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
    if getattr(sys, "frozen", False):
        return os.path.abspath(sys.executable)
    return os.path.abspath(sys.argv[0])

def extract_unc_server(path):
    if not path: return None
    p = path.strip().strip('"')
    if not p.startswith("\\\\"): return None
    parts = p[2:].split("\\", 1)
    if not parts or not parts[0]: return None
    return parts[0]

def configure_unc_as_intranet(server):
    if not server: return False
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, ZONE_MAP_POLICY) as key:
            winreg.SetValueEx(key, "UNCAsIntranet", 0, winreg.REG_DWORD, 1)
        for base in (ZONE_MAP_DOMAINS, ZONE_MAP_ESC_DOMAINS):
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "{}\\{}".format(base, server)) as key:
                winreg.SetValueEx(key, "file", 0, winreg.REG_DWORD, 1)
        return True
    except Exception:
        return False

def get_datamatrix_prefix(filename):
    name = os.path.splitext(filename)[0]
    return name.split("_", 1)[0].strip()

def count_all_files(folder):
    if not folder or not os.path.exists(folder): return 0
    try:
        # Adaptado a OS.LISTDIR (Compatible con Python 3.4 y XP)
        return sum(1 for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)))
    except Exception:
        return 0

def count_unique_datamatrix(folder):
    if not folder or not os.path.exists(folder): return 0
    try:
        latest = {}
        # Adaptado a OS.LISTDIR y OS.STAT (Compatible con XP)
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            if not os.path.isfile(path) or not f.lower().endswith(".xml"):
                continue
            prefix = get_datamatrix_prefix(f)
            ctime = os.stat(path).st_mtime
            if prefix not in latest or ctime > latest[prefix]:
                latest[prefix] = ctime
        return len(latest)
    except Exception:
        return 0

def detect_snap_edges():
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
    x, y   = window.winfo_x(), window.winfo_y()
    w, h   = window.winfo_width(), window.winfo_height()
    sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()

    if   snap_x == "left":   x = 0
    elif snap_x == "right":  x = sw - w
    if   snap_y == "top":    y = 0
    elif snap_y == "bottom": y = sh - h

    window.geometry("+{}+{}".format(x, y))

def apply_window_size_for(value):
    detect_snap_edges()
    preset = SIZE_BY_DIGITS.get(min(len(str(value)), 5), SIZE_BY_DIGITS[1])
    window.geometry("{}x{}".format(preset['width'], preset['height']))
    label.configure(font=("Segoe UI", preset["font"], "bold"))
    window.update_idletasks()
    apply_snap_edges()

def apply_theme():
    theme = th()
    window.configure(bg=theme["bg"])
    label.configure(bg=theme["bg"])
    # Forzar actualización del color actual si no estamos en error/éxito
    if label.cget("fg") not in (SUCCESS_COLOR, ERROR_COLOR):
        label.configure(fg=theme["fg"])

def update_counter():
    if not origin_folder or not os.path.exists(origin_folder):
        label.configure(text="ERR", fg=ERROR_COLOR)
        window.after(INTERVAL_MS, update_counter)
        return

    value = count_unique_datamatrix(origin_folder) if unique_mode else count_all_files(origin_folder)

    if target_value is None or value < target_value:
        text_color = th()["fg"]
    elif value == target_value:
        text_color = SUCCESS_COLOR
    else:
        text_color = ERROR_COLOR

    label.configure(text=str(value), fg=text_color)

    global _last_digits
    current_digits = len(str(value))
    if current_digits != _last_digits:
        apply_window_size_for(value)
        _last_digits = current_digits

    window.after(INTERVAL_MS, update_counter)

def _center_on_screen(win):
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    w, h   = win.winfo_width(), win.winfo_height()
    win.geometry("+{}+{}".format((sw - w) // 2, (sh - h) // 2))

def show_input_dialog(title, question, callback):
    was_topmost = window.attributes("-topmost")
    window.attributes("-topmost", False)

    dialog = tk.Toplevel(window)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.attributes("-topmost", True)
    dialog.configure(bg=th()["bg"])
    dialog.grab_set()
    
    dialog.geometry("300x180")

    tk.Label(dialog, text=title, font=("Segoe UI", 12, "bold"), bg=th()["bg"], fg=th()["fg"]).pack(pady=(20, 5))
    tk.Label(dialog, text=question, font=("Segoe UI", 10), bg=th()["bg"], fg=th()["fg"]).pack(pady=(0, 10))

    entry = tk.Entry(dialog, width=10, font=("Segoe UI", 14), justify="center")
    entry.pack(pady=5)
    entry.focus_force()

    btn_frame = tk.Frame(dialog, bg=th()["bg"])
    btn_frame.pack(pady=15)

    def on_confirm(*args):
        try:
            val = int(entry.get())
            if val >= 1:
                window.attributes("-topmost", was_topmost)
                dialog.destroy()
                callback(val)
        except ValueError:
            entry.configure(bg=ERROR_COLOR, fg="white")

    def on_cancel(*args):
        window.attributes("-topmost", was_topmost)
        dialog.destroy()

    tk.Button(btn_frame, text=t("confirm"), command=on_confirm, width=10, bg=th()["btn_bg"], fg=th()["btn_fg"], relief="flat").pack(side="left", padx=5)
    tk.Button(btn_frame, text=t("cancel"), command=on_cancel, width=10, bg=th()["btn_bg"], fg=th()["btn_fg"], relief="flat").pack(side="left", padx=5)

    dialog.bind("<Return>", on_confirm)
    dialog.bind("<Escape>", on_cancel)

    _center_on_screen(dialog)

def show_about():
    about = tk.Toplevel(window)
    about.title(t("about"))
    about.resizable(False, False)
    about.attributes("-topmost", True)
    about.configure(bg=th()["bg"])
    about.geometry("300x200")

    tk.Label(about, text=APP_NAME, font=("Segoe UI", 16, "bold"), bg=th()["bg"], fg=th()["fg"]).pack(pady=(20, 0))
    tk.Label(about, text="v{}".format(APP_VERSION), font=("Segoe UI", 9), bg=th()["bg"], fg=th()["fg"]).pack()
    tk.Label(about, text=t("app_description"), font=("Segoe UI", 10), bg=th()["bg"], fg=th()["fg"]).pack(pady=15)
    tk.Label(about, text=APP_AUTHOR, font=("Segoe UI", 9), bg=th()["bg"], fg="gray").pack()
    tk.Button(about, text=t("close"), command=about.destroy, width=15, bg=th()["btn_bg"], fg=th()["btn_fg"], relief="flat").pack(pady=10)

    _center_on_screen(about)

def show_context_menu(event):
    # Uso un Menu nativo estándar (Lo más fiable para XP y Tkinter)
    menu = tk.Menu(window, tearoff=0, bg=th()["menu_bg"], fg=th()["menu_fg"])
    
    # Variables actualizadas en caliente
    window.var_topmost.set(bool(window.attributes("-topmost")))
    window.var_titlebar.set(titlebar_visible)
    window.var_dark.set(dark_mode)
    window.var_unique.set(unique_mode)
    window.var_startup.set(is_startup_enabled())

    menu.add_checkbutton(label=t("always_on_top"), variable=window.var_topmost, command=toggle_topmost)
    menu.add_checkbutton(label=t("windows_bar"), variable=window.var_titlebar, command=toggle_titlebar)
    menu.add_checkbutton(label=t("dark_mode"), variable=window.var_dark, command=toggle_dark_mode)
    menu.add_checkbutton(label=t("unique_mode"), variable=window.var_unique, command=toggle_unique_mode)
    menu.add_checkbutton(label=t("start_with_windows"), variable=window.var_startup, command=toggle_startup_with_windows)
    
    menu.add_separator()
    t_val = target_value if target_value else 'None'
    menu.add_command(label="{}: {}".format(t("target"), t_val), command=set_target_value)
    
    # Submenú Idioma
    lang_menu = tk.Menu(menu, tearoff=0, bg=th()["menu_bg"], fg=th()["menu_fg"])
    lang_menu.add_command(label=t("lang_es"), command=lambda: set_language("es"))
    lang_menu.add_command(label=t("lang_en"), command=lambda: set_language("en"))
    lang_menu.add_command(label=t("lang_eu"), command=lambda: set_language("eu"))
    menu.add_cascade(label=t("language"), menu=lang_menu)
    
    menu.add_separator()
    menu.add_command(label=t("about"), command=show_about)
    menu.add_command(label=t("close"), command=close_app)

    menu.post(event.x_root, event.y_root)

def toggle_topmost():
    window.attributes("-topmost", window.var_topmost.get())

def toggle_titlebar():
    global titlebar_visible
    titlebar_visible = window.var_titlebar.get()
    window.overrideredirect(not titlebar_visible)
    if titlebar_visible:
        # Recuperar foco forzosamente
        current_topmost = window.attributes("-topmost")
        window.after(50, lambda: window.attributes("-topmost", current_topmost))

def toggle_dark_mode():
    global dark_mode
    dark_mode = window.var_dark.get()
    apply_theme()

def toggle_unique_mode():
    global unique_mode
    unique_mode = window.var_unique.get()

def toggle_startup_with_windows():
    enable = window.var_startup.get()
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
            parent=window
        )
    else:
        messagebox.showerror(t("startup_confirm_title"), t("startup_error"), parent=window)

def set_language(lang):
    global current_lang
    current_lang = lang

def ask_target_on_startup():
    show_input_dialog(t("startup_title"), t("startup_question"), _apply_target)

def set_target_value():
    show_input_dialog(t("target_title"), t("target_question"), _apply_target)

def _apply_target(value):
    global target_value
    target_value = value

def close_app():
    window.destroy()

drag_offset = {"x": 0, "y": 0}

def start_drag(event):
    drag_offset["x"] = event.x
    drag_offset["y"] = event.y

def on_drag(event):
    nx = window.winfo_pointerx() - drag_offset["x"]
    ny = window.winfo_pointery() - drag_offset["y"]
    window.geometry("+{}+{}".format(nx, ny))

def on_release(event):
    detect_snap_edges()
    apply_snap_edges()

# =====================
# CONSTRUCCIÓN CONTADOR
# =====================
window = tk.Tk()
window.title(APP_NAME)
window.geometry("128x128")
window.minsize(*MIN_SIZE)
window.maxsize(*MAX_SIZE)
window.attributes("-topmost", True)
window.overrideredirect(True)

# Variables de control para el menú de Tkinter
window.var_topmost = tk.BooleanVar()
window.var_titlebar = tk.BooleanVar()
window.var_dark = tk.BooleanVar()
window.var_unique = tk.BooleanVar()
window.var_startup = tk.BooleanVar()

label = tk.Label(
    window,
    text="0",
    font=("Segoe UI", 60, "bold") # En XP, si no tiene Segoe UI, caerá suavemente a Tahoma/Arial
)
label.place(relx=0.5, rely=0.5, anchor="center")

window.bind("<Button-3>",        show_context_menu)
label.bind("<Button-3>",         show_context_menu)
window.bind("<Button-1>",        start_drag)
label.bind("<Button-1>",         start_drag)
window.bind("<B1-Motion>",       on_drag)
label.bind("<B1-Motion>",        on_drag)
window.bind("<ButtonRelease-1>", on_release)
label.bind("<ButtonRelease-1>",  on_release)

load_config()
apply_theme()

window.after(0, lambda: window.geometry(
    "+{}+0".format(window.winfo_screenwidth() - window.winfo_width())
))

window.after(100, ask_target_on_startup)
update_counter()

window.mainloop()