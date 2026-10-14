import requests 
import re
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, simpledialog, ttk
from models import ChessRecord, Session, reset_chess_records
from OnlineChessAPI import map_result_for_player
from datetime import datetime, timezone, date
from sqlalchemy import text

# App Constants
APP_TITLE = "Chess Game Record - Chess.com"
USER_AGENT = "ChessRecordApp/1.0 (contact: (email address)"
MONTHS_TO_FETCH = 1
LISTBOX_HEIGHT = 14
PAD = 10

COLUMNS=("id", "date", "opponent", "result") # Treeview column order
VALID_RESULTS=("Win", "Lost")

class ChessApp:
    """
    Desktop app (Tkinter) to track Chess.com matches.
    - Basic CRUD functionality (add, edit, delete results)
    - Synchronization with the Chess.com public API (wins/losses)
    - Totals displayed at the top (Wins | Losses)
    - Button to clear all data (reset)
    """

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)  
        self.root.minsize(680, 420)
        self._setup_style()

        # Create a SQLAlchemy session (imported from models.py)
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

        #----UI: Totals--------
        # Top label showing the win/loss count 
        self.totals_lbl = ttk.Label(header, text="Wins: 0 | Losses: 0", style="Header.TLabel")
        self.totals_lbl.grid(row=0, column=0, sticky="w")   

    def _build_body(self) -> None:
        #---Body: List---
        body = ttk.Frame(self.root, padding=(PAD, 0, PAD, PAD))
        body.grid(row=1, column=0, sticky="nsew")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Treeview with columns
        self.tree = ttk.Treeview(
            body,
            columns=COLUMNS,
            show="headings",
            selectmode="browse",
            height=LISTBOX_HEIGHT
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("opponent", text="Opponent")
        self.tree.heading("result", text="Result")

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
        ttk.Button(btns, text="Add Win", command=lambda: self.open_add_dialog("Win")).grid(row=0, column=0, padx=(0,6))
        ttk.Button(btns, text="Add Loss", command=lambda: self.open_add_dialog("Loss")).grid(row=0, column=1, padx=6)
        ttk.Button(btns, text="Edit", command=self.open_edit_dialog).grid(row=0, column=2, padx=6)
        ttk.Button(btns, text="Delete", command=self.delete_selected).grid(row=0, column=3, padx=6)
        ttk.Button(btns, text="Synchronize Chess.com", command=self.sync_from_chesscom).grid(row=0, column=4, padx=6)
        ttk.Button(btns, text="Reset (Delete everything)", command=self.reset_all_records).grid(row=0, column=5, padx=(6,0))
         
        btns.grid_columnconfigure(6, weight=1)
        
    def refresh_table(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            records=self.session.query(ChessRecord).order_by(ChessRecord.id).all()
            for rec in records:
                self.tree.insert("", "end", iid=str(rec.id), values=(rec.id, rec.date or "", rec.opponent or "", rec.result))
        except Exception as e:
            messagebox.showerror("DB", f"Records could not be read:\n{e}")
            return
    
        self.update_totals()

    def update_totals(self):
        """
        Update the win/loss totals
        """
        try:
            g = self.session.query(ChessRecord).filter(ChessRecord.result == "Win").count()
            p = self.session.query(ChessRecord).filter(ChessRecord.result == "Loss").count()  
            self.totals_lbl.config(text=f"Ganadas: {g} | Perdidas: {p}")
        except Exception:
             # If there is a connection error, don't break the UI
             pass
    
    def open_add_dialog(self, default_result: str | None = None) -> None:
        self._open_record_dialog(title="Add record", default_result=default_result)

    def open_edit_dialog(self) -> None:
        rec=self._get_selected_record()    
        if not rec:
            messagebox.showwarning("Edit", "Select a record")
            return
        self._open_record_dialog(title="Edit record", record=rec)

    def _open_record_dialog(self, title: str, record: ChessRecord | None = None, default_result: str | None = None) -> None:
        """
        Create a simple dialog (Toplevel) for adding/editing
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

        result_var = tk.StringVar(value=(record.result if record else (default_result or "Win")))
        result_cb = ttk.Combobox(frm, textvariable=result_var, values=VALID_RESULTS, state="readonly", width = 14)
        result_cb.grid(row=0, column=1, sticky="w", pady=3)

        ttk.Label(frm, text="Opponent:").grid(row=1, column=0, sticky="w")

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
                messagebox.showerror("Validation", "Result must be 'Win' or 'Loss'.", parent=dlg)
                return
            
            d = date_var.get().strip()
            if d and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
                messagebox.showerror("Validation", "Invalid date. Use format YYYY-MM-DD.", parent=dlg)
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
                messagebox.showerror("DB", f"Could not be saved:\n{e}", parent=dlg)

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
            messagebox.showwarning("Delete", "Select a record")
            return
        if not messagebox.askyesno("Confirm", f"Delete record #{rec.id}?", default="no"):
            return
        try:
            self.session.delete(rec)
            self.session.commit()
            self.refresh_table()
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("DB", f"Could not be deleted:\n{e}")

    def reset_all_records(self):
        """
        Deletes all database records after asking for confirmation.
        (Useful for starting from scratch or if synchronization failed)
        """
        if not messagebox.askyesno(
            "Confirm",
            "This will delete ALL records (wins/losses) from the database and reset the IDs. Continue?"
        ):
            return
        try: 
            self.session.execute(text("TRUNCATE TABLE chess_records RESTART IDENTITY"))
            self.session.commit()

            # Invalidates the ORM identity map/cache to avoid seeing "phantom" rows
            self.session.expire_all()
            # Refresh
            self.refresh_table()

            messagebox.showinfo("Done", "All records were deleted and the IDs were reset.")
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"Could not delete the records: {e}")

    
    def on_close(self):
        """
        Clean shutdown: closes the SQLAlchemy database session and destroys the window
        """
        try:
            self.session.close()
        finally:
            self.root.destroy()

    def _setup_style(self) -> None:
        """
        Configures base styles for ttk and the default font. 
        Attempts to use a pleasant theme if available
        """
        try:
            # Default font for (almost) all widgets (tk and ttk)
            # Will affect widgets created after this call
            self.root.option_add('*Font', '{Segoe UI} 10') # Change it for the one you prefer
            style = ttk.Style(self.root)


            # Select an available topic (in order of preference)
            preferred = ('view', 'xpnative', 'clam', 'default')
            available = style.theme_names()
            for t in preferred:
                if t in available:
                    style.theme_use(t)
                    break
            
            # Adjust default Tk fonts (not loose strings)
            for fname in ("TkDefaultFont", "TkTextFont", "TkHeadingFont", "TkMenuFont"):
                try:
                    f = tkfont.nametofont(fname)
                    f.configure(family="Segoe UI", size=10) # or the family you prefer
                except tk.TclError:
                    pass

            # Create a named font (avoids the issue with "Segoe UI")
            header_font = tkfont.Font(family="Segoe UI", size = 10, weight="bold")

            # Fine-tuning for buttons and labels
            style.configure('TButton', padding=(10,6))
            style.configure('TLabel', padding=(0,2))
            style.configure('Header.TLabel', font=header_font)

            style.configure("Treeview", rowheight=24)
            style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        except Exception: 
            # If something fails (theme unavailable, etc.), we fall back to the default values.
            pass
    


    # Synchronization with Chess.com
    def sync_from_chesscom(self):
        """
        Request the username, query the public Chess.com API, and add all 'Win' or 'Loss' games from the last N months to the database
        (Draws are ignored for now; you can handle them in OnlineChessAPI.py)
        """
        username = simpledialog.askstring("Chess.com", "Your Chess.com username (exact):") 
        if not username:
            return  # Canceled
        
        # Improtant: Add a User-Agent with contact information in case Chess.com blocks the request
        headers = {
            "User-Agent": USER_AGENT
        }


        try: 
            # 1) Get list of monthly files
            url_archives = f"https://api.chess.com/pub/player/{username}/games/archives"
            r = requests.get(url_archives, headers=headers, timeout=20)

            # Errores típicos
            if r.status_code == 403:
                messagebox.showerror("API 403", "Chess.com rejected the request. Add a User-Agent with contact information")
                return
            if r.status_code == 404:
                messagebox.showerror("User not found", f"The user '{username}' was not found on Chess.com.")
                return
            r.raise_for_status()
            archives = r.json().get("archives", [])
            print("Num archives:" , len(archives))
            if not archives:
                messagebox.showinfo("No data", f"No match files for '{username}'.")
                return
        
           
            month_urls = archives[-MONTHS_TO_FETCH:]
            print("Processing months:", month_urls)

            # Feedback counters
            inserted = 0
            scanned = 0
            wins = 0
            losses = 0
            draws = 0 

            # Go through each month and its line items
            for month_url in month_urls:
                print("GET month:", month_url)
                m = requests.get(month_url, headers=headers, timeout=30)
                print("Status month:", m.status_code)
                if m.status_code == 403:
                    messagebox.showerror("API 403", "Chess.com rejected a monthly download. Check the User-Agent ratio.")
                    return 
                m.raise_for_status()
                games = m.json().get("games", [])
                print(f"Matches in {month_url}:", len(games))

                for g in games:
                    scanned += 1 # Counts scanned matches
                    
                    # Mape result for 'username' -> "Win"/"Loss"/None
                    outcome = map_result_for_player(g, username)
                    if outcome is None:
                        continue # We disregard draws/other states

                    # Counters for detected (not inserted) wins/losses
                    if outcome == "Win":
                        wins += 1
                    elif outcome == "Loss":
                        losses += 1
                    
                    # Date: we will use end_time (epoch) if it exists
                    end_ts = g.get("end_time")
                    date_str = datetime.fromtimestamp(end_ts, tz=timezone.utc).strftime("%Y-%m-%d") if end_ts else ""
                
                    # Opponent (Determined within the helper; repeated here for simplicity)
                    white = g.get("white", {})
                    black = g.get("black", {})
                    if white.get("username", "").lower() == username.lower():
                        opponent = black.get("username")
                    else:
                        opponent = white.get("username")

                    # Avoid basic duplicates: (opponent, result, date)
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
            
            # Persist changes and refresh UI
            self.session.commit()
            self.refresh_table()
            messagebox.showinfo("Synchronization complete", f"{inserted} matches (Win/Loss) were inserted.")

            # Visible summary: (in both the messagebox and the console)
            msg = [
                f"Scanned: {scanned}",
                f"Wins detected: {wins}",
                f"Losses detected: {losses}",
                f"Draws detected: {draws}",
                f"New entries inserted: {inserted}"
            ]
            messagebox.showinfo("Synchronization Chess.com", "\n".join(msg))
            print("\n".join(msg))

            # Additional message if nothing was inserted
            if inserted == 0:
                messagebox.showinfo(
                    "No new matches",
                    "No new matches were inserted.\n"
                    "- They might all have been draws (currently ignored),\n"
                    "- or they were already recorded (deduplication),\n"
                    "- or there are no games in the most recently processed months."
                )

        except requests.RequestException as e:
            # Network errors (timeout, DNS, etc.)
            messagebox.showerror("Network", f"Network error querying Chess.com: {e}")        
            print("Network error:", e)
        except Exception as e:
            # Other errors: roll bacj transaction and report
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred while synchronizing: {e}")
            print("Sync error:", e)

# Entry point: creates the Tkinter root (Tk) and launches the app.
if __name__ == "__main__":
    reset_chess_records(start_at_zero=False) 
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()

