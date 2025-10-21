import requests 
import re
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, simpledialog, ttk
from models import ChessRecord, Session, reset_chess_records
from OnlineChessAPI import map_result_for_player
from datetime import datetime, timezone, date
from sqlalchemy import text

# Constantes de la App
APP_TITLE = "Registro de Partidas de Ajedrez - Chess.com"
USER_AGENT = "ChessRecordApp/1.0 (contacto: paradigmshiftzu09@gmail.com)"
MONTHS_TO_FETCH = 1
LISTBOX_HEIGHT = 14
PAD = 10

COLUMNS=("id", "date", "opponent", "result") # Orden de columnas del Treeview
VALID_RESULTS=("Ganada", "Perdida")

class ChessApp:
    """
    App de escritorio (Tkinter) para llevar un registro de partidas de Chess.com.
    - CRUD básico (agregar, editar, eliminar resultados)
    - Sincronización con la API pública de Chess.com (ganadas/perdidas)
    - Totales en la parte superior (Ganadas | Perdidas).
    - Botón para vaciar todo (reset).
    """

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)  
        self.root.minsize(680, 420)
        self._setup_style()

        # Crea una sesión de SQLAlchemy (se importa de models.py)
        self.session = Session()
        
        # --- Layout: header / body / footer ---
        self._build_header()
        self._build_body()
        self._build_buttons()

        self.refresh_table()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_header(self) -> None:
         # Cabecera
        header = ttk.Frame(self.root, padding=PAD)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        #----UI: Totales--------
        # Etiqueta superior que muestra el conteo de ganadas y perdidas 
        self.totals_lbl = ttk.Label(header, text="Ganadas: 0 | Perdidas: 0", style="Header.TLabel")
        self.totals_lbl.grid(row=0, column=0, sticky="w")   

    def _build_body(self) -> None:
        #---Cuerpo: Listado---
        body = ttk.Frame(self.root, padding=(PAD, 0, PAD, PAD))
        body.grid(row=1, column=0, sticky="nsew")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Treeview con columnas
        self.tree = ttk.Treeview(
            body,
            columns=COLUMNS,
            show="headings",
            selectmode="browse",
            height=LISTBOX_HEIGHT
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Fecha")
        self.tree.heading("opponent", text="Oponente")
        self.tree.heading("result", text="Resultado")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("opponent", width=220, anchor="w")
        self.tree.column("result", width=120, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        vscroll = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        vscroll.grid(row=0, column=1, sticky="ns", padx=(5,0))
        self.tree.configure(yscrollcommand=vscroll.set)

        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

    def _build_buttons(self) -> None:
        btns = ttk.Frame(self.root, padding=(PAD, 0, PAD, PAD))
        btns.grid(row=2, column=0, sticky="ew")

         # ----UI: Botones------
        ttk.Button(btns, text="Agregar Ganada", command=lambda: self.open_add_dialog("Ganada")).grid(row=0, column=0, padx=(0,6))
        ttk.Button(btns, text="Agregar Perdida", command=lambda: self.open_add_dialog("Perdida")).grid(row=0, column=1, padx=6)
        ttk.Button(btns, text="Editar", command=self.open_edit_dialog).grid(row=0, column=2, padx=6)
        ttk.Button(btns, text="Eliminar", command=self.delete_selected).grid(row=0, column=3, padx=6)
        ttk.Button(btns, text="Sincronizar Chess.com", command=self.sync_from_chesscom).grid(row=0, column=4, padx=6)
        ttk.Button(btns, text="Reset (Borrar Todo)", command=self.reset_all_records).grid(row=0, column=5, padx=(6,0))
         
        btns.grid_columnconfigure(6, weight=1)
        
    def refresh_table(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            records=self.session.query(ChessRecord).order_by(ChessRecord.id).all()
            for rec in records:
                self.tree.insert("", "end", iid=str(rec.id), values=(rec.id, rec.date or "", rec.opponent or "", rec.result))
        except Exception as e:
            messagebox.showerror("DB", f"No se pudieron leer registros:\n{e}")
            return
    
        self.update_totals()

    def update_totals(self):
        """
        Actualiza los totales de ganadas/perdidas
        """
        try:
            g = self.session.query(ChessRecord).filter(ChessRecord.result == "Ganada").count()
            p = self.session.query(ChessRecord).filter(ChessRecord.result == "Perdida").count()  
            self.totals_lbl.config(text=f"Ganadas: {g} | Perdidas: {p}")
        except Exception:
             # Si hay error de conexión, no rompas la UI
             pass
    
    def open_add_dialog(self, default_result: str | None = None) -> None:
        self._open_record_dialog(title="Agregar registro", default_result=default_result)

    def open_edit_dialog(self) -> None:
        rec=self._get_selected_record()    
        if not rec:
            messagebox.showwarning("Editar", "Seleccione un registro.")
            return
        self._open_record_dialog(title="Editar registro", record=rec)

    def _open_record_dialog(self, title: str, record: ChessRecord | None = None, default_result: str | None = None) -> None:
        """
        Crea un diálogo simple (Toplevel) para agregar/editar
        """
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.transient(self.root)
        dlg.grab_set() # Modal
        dlg.resizable(False, False)
        pad=12

        frm = ttk.Frame(dlg, padding=pad)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="Resultado:").grid(row=0, column=0, sticky="w")

        result_var = tk.StringVar(value=(record.result if record else (default_result or "Ganada")))
        result_cb = ttk.Combobox(frm, textvariable=result_var, values=VALID_RESULTS, state="readonly", width = 14)
        result_cb.grid(row=0, column=1, sticky="w", pady=3)

        ttk.Label(frm, text="Oponente:").grid(row=1, column=0, sticky="w")

        opp_var = tk.StringVar(value=(record.opponent if record else ""))
        opp_entry = ttk.Entry(frm, textvariable=opp_var, width=28)
        opp_entry.grid(row=1, column=1, sticky="w", pady=3)

        ttk.Label(frm, text="Fecha (YYYY=MM-DD):").grid(row=2, column=0, sticky="w")
        date_var = tk.StringVar(value=(record.date if record and record.date else date.today().isoformat()))
        date_entry = ttk.Entry(frm, textvariable=date_var, width=16)
        date_entry.grid(row=2, column=1, sticky="w", pady=3)

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=2, pady=(pad,0), sticky="e")

        def on_accept():
            res = result_var.get()
            if res not in VALID_RESULTS:
                messagebox.showerror("Validación", "Resultado debe ser 'Ganada' o 'Perdida'.", parent=dlg)
                return
            
            d = date_var.get().strip()
            if d and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
                messagebox.showerror("Validación", "Fecha inválida. Usa formato YYYY-MM-DD.", parent=dlg)
                return
            
            opp = opp_var.get().strip() or None

            try:
                if record:
                    record.result = res
                    record.opponent = opp
                    record.date = d or None
                else:
                    self.session.add(ChessRecord(result=res, opponent=opp, date=d or None))
                self.session.commit()
                self.refresh_table()
                dlg.destroy()
            except Exception as e:
                self.session.rollback()
                messagebox.showerror("DB", f"No se pudo guardar:\n{e}", parent=dlg)

        def on_cancel():
            dlg.destroy()

        ttk.Button(btns, text="Cancelar", command=on_cancel).grid(row=0, column=0, padx=(0,6))
        ttk.Button(btns, text="Guardar", command=on_accept).grid(row=0, column=1)

        # Enfoque inicial
        (opp_entry if not record else result_cb).focus_set()
        self.root.wait_window(dlg)

    def _get_selected_record(self) -> ChessRecord | None:
        sel = self.tree.selection()
        if not sel:
            return None
        rec_id = int(sel[0])
        try:
            rec = self.session.get(ChessRecord, rec_id)
            return rec
        except Exception:
            return None

    def delete_selected(self) -> None:
        rec = self._get_selected_record()
        if not rec:
            messagebox.showwarning("Eliminar", "Selecciona un registro")
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar registro #{rec.id}?", default="no"):
            return
        try:
            self.session.delete(rec)
            self.session.commit()
            self.refresh_table()
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("DB", f"No se pudo eliminar:\n{e}")

    def reset_all_records(self):
        """
        Borra todos los registros de la base de datos tras pedir confirmación.
        (Útil para empezar de cero o si la sincronización falló)
        """
        if not messagebox.askyesno(
            "Confirmar",
            "Esto borrará TODOS los registros (ganadas/perdidas) de la base de datos y reiniciará los IDs. ¿Continuar?"
        ):
            return
        try: 
            self.session.execute(text("TRUNCATE TABLE chess_records RESTART IDENTITY"))
            self.session.commit()

            # Invalida el identity map / caché del ORM para no ver filas "fantasma"
            self.session.expire_all()
            # Refrescar
            self.refresh_table()

            messagebox.showinfo("Listo", "Se borraron todos los registros y se reiniciaron los IDs.")
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"No se pudo borrar los registros: {e}")

    
    def on_close(self):
        """
        Cierre limpio: cierra la sesión de la base de datos de SQLAlchemy y destruye la ventana
        """
        try:
            self.session.close()
        finally:
            self.root.destroy()

    def _setup_style(self) -> None:
        """
        Configura estilos base para ttk y fuente por defecto.
        Intenta usar un tema agradable si está disponible.
        """
        try:
            # Fuente por defecto para (casi) todos los widgets (tk y ttk)
            # Afectará widgets creados después de esta llamada
            self.root.option_add('*Font', '{Segoe UI} 10') # Cambia por la que prefieras
            style = ttk.Style(self.root)


            # Selecciona un tema disponible (orden de preferencia)
            preferred = ('vista', 'xpnative', 'clam', 'default')
            available = style.theme_names()
            for t in preferred:
                if t in available:
                    style.theme_use(t)
                    break
            
            # Ajustar fuentes por defecto de Tk (no cadenas sueltas)
            for fname in ("TkDefaultFont", "TkTextFont", "TkHeadingFont", "TkMenuFont"):
                try:
                    f = tkfont.nametofont(fname)
                    f.configure(family="Segoe UI", size=10) # o la familia que prefieras
                except tk.TclError:
                    pass

            # Crea una fuente nombrada (evita el problema con "Segoe UI")
            header_font = tkfont.Font(family="Segoe UI", size = 10, weight="bold")

            # Ajustes suaves para botones y etiquetas 
            style.configure('TButton', padding=(10,6))
            style.configure('TLabel', padding=(0,2))
            style.configure('Header.TLabel', font=header_font)

            style.configure("Treeview", rowheight=24)
            style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        except Exception: 
            # Si algo falla (tema no disponible, etc.), seguimos con los valores por defecto
            pass
    


    # Sincronización con Chess.com
    def sync_from_chesscom(self):
        """
        Pide el username, consulta la API pública de Chess.com y agrega a la BD
        todas las partidas 'Ganada' o 'Perdida' de los últimos N meses.
        (Empates se ignoran por ahora; puedes activarlos en OnlineChessAPI.py)
        """
        username = simpledialog.askstring("Chess.com", "Tu username de Chess.com (exacto):") 
        if not username:
            return  # Cancelado
        
        # Importante: agrega un User-Agent con contacto en caso de que Chess.com bloquee la solicitud
        headers = {
            "User-Agent": USER_AGENT
        }


        try: 
            # 1) Obtener Lista de archivos mensuales
            url_archives = f"https://api.chess.com/pub/player/{username}/games/archives"
            r = requests.get(url_archives, headers=headers, timeout=20)

            # Errores típicos
            if r.status_code == 403:
                messagebox.showerror("API 403", "Chess.com rechazó la solicitud. Agrega un User-Agent con contacto.")
                return
            if r.status_code == 404:
                messagebox.showerror("Usuario no encontrado", f"No se encontró el usuario '{username}' en Chess.com.")
                return
            r.raise_for_status()
            archives = r.json().get("archives", [])
            print("Num archives:" , len(archives))
            if not archives:
                messagebox.showinfo("Sin datos", f"No hay archivos de partidas para '{username}'.")
                return
        
           
            month_urls = archives[-MONTHS_TO_FETCH:]
            print("Procesando meses:", month_urls)

            # Contadores para feedback
            inserted = 0
            scanned = 0
            wins = 0
            losses = 0
            draws = 0 

            # Recorre cada mes y sus partidas
            for month_url in month_urls:
                print("GET month:", month_url)
                m = requests.get(month_url, headers=headers, timeout=30)
                print("Status month:", m.status_code)
                if m.status_code == 403:
                    messagebox.showerror("API 403", "Chess.com rechazó una descarga mensual. Revisa el User-Agent/ratio.")
                    return 
                m.raise_for_status()
                games = m.json().get("games", [])
                print(f"Partidas en {month_url}:", len(games))

                for g in games:
                    scanned += 1 # Cuenta las partidas escaneadas
                    
                    # Mapear resultado para 'username' -> "Ganada"/"Perdida"/None
                    outcome = map_result_for_player(g, username)
                    if outcome is None:
                        continue # Ignoramos empates/otros estados

                    # Contadores de wins/losses detectadas (no insertadas)
                    if outcome == "Ganada":
                        wins += 1
                    elif outcome == "Perdida":
                        losses += 1
                    
                    # Fecha: usaremos end_time (epoch) si existe
                    end_ts = g.get("end_time")
                    date_str = datetime.fromtimestamp(end_ts, tz=timezone.utc).strftime("%Y-%m-%d") if end_ts else ""
                
                    # Oponente (Lo determinamos dentro del helper; repetimos aquí por simplicidad)
                    white = g.get("white", {})
                    black = g.get("black", {})
                    if white.get("username", "").lower() == username.lower():
                        opponent = black.get("username")
                    else:
                        opponent = white.get("username")

                    # Evitar duplicados básicos: (opponent, result, date)
                    exists = (
                        self.session.query(ChessRecord)
                        .filter(
                            ChessRecord.opponent == opponent,
                            ChessRecord.result == outcome,
                            ChessRecord.date == date_str  
                        )
                        .first()
                    )
                    if not exists:
                        self.session.add(ChessRecord(opponent=opponent, result=outcome, date=date_str))
                        inserted +=1
            
            # Persistir cambios y refrescar UI
            self.session.commit()
            self.refresh_table()
            messagebox.showinfo("Sincronización Completa", f"Se insertaron {inserted} partidas (Ganada/Perdida).")

            # Resumen visible: (tanto en messagebox como en consola)
            msg = [
                f"Escaneadas: {scanned}",
                f"Wins detectadas: {wins}",
                f"Losses detectadas: {losses}",
                f"Empates detectados: {draws}",
                f"Nuevos insertados: {inserted}"
            ]
            messagebox.showinfo("Sincronización Chess.com", "\n".join(msg))
            print("\n".join(msg))

            # Mensaje adicional si no insertó nada
            if inserted == 0:
                messagebox.showinfo(
                    "Sin partidas nuevas",
                    "No se insertaron partidas nuevas.\n"
                    "- Puede que todas fueran empates (actualmente ignorados),\n"
                    "- o que ya estuvieran registradas (deduplicación),\n"
                    "- o que no haya partidas en los últimos meses procesados."
                )

        except requests.RequestException as e:
            # Errores de red (timeout, DNS, etc.)
            messagebox.showerror("Red", f"Error de red al consultar Chess.com: {e}")        
            print("Network error:", e)
        except Exception as e:
            # Otros errores: deshacer transacción e informar
            self.session.rollback()
            messagebox.showerror("Error", f"Ocurrió un error al sincronizar: {e}")
            print("Sync error:", e)

# Punto de entrada: crea la raíz de Tkinter (Tk) y arranca la app
if __name__ == "__main__":
    reset_chess_records(start_at_zero=False) 
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()

