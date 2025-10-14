import tkinter as tk
from tkinter import messagebox, simpledialog
from models import ChessRecord, Session

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro de Partidas de Ajedrez - Chess.com")  
        self.session = Session()
        
        # Totales 
        self.lbl_totals = tk.Label(root, text="Ganadas: 0 | Perdidas: 0")
        self.lbl_totals.pack(pady=(10,0), anchor="w")

        # Lista
        self.listbox = tk.Listbox(root, width=40)
        self.listbox.pack(pady=10)

        self.refresh_list()

        btn_frame = tk.Frame(root)
        btn_frame.pack()

        tk.Button(btn_frame, text="Agregar Ganada", command=lambda: self.add_record("Ganada")).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Agregar Perdida", command=lambda: self.add_record("Perdida")).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Editar", command=self.edit_record).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Eliminar", command=self.delete_record).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Sincronizar Chess.com", command=self.sync_from_chesscom).grid(row=0, column=4, padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    def refresh_list(self):
        self.listbox.delete(0, tk.END)

        try:
             records = self.session.query(ChessRecord).all()
        except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer registros: {e}")
                return

        for record in records:
            self.listbox.insert(tk.END, f"{record.id}: {record.result}")
        
        self.update_totals()

    def update_totals(self):
        try:
            g = self.session.query(ChessRecord).filter(ChessRecord.result == "Ganada").count()
            p = self.session.query(ChessRecord).filter(ChessRecord.result == "Perdida").count()  
            self.lbl_totals.config(text=f"Ganadas: {g} | Perdidas: {p}")
        except Exception:
             # Si hay error de conexión, no rompas la UI
             pass
            
             
    def add_record(self, result):
        if result not in ("Ganada", "Perdida"):
             messagebox.showerror("Error", "Resultado inválido")
             return
        try:
             new_record = ChessRecord(result=result) 
             self.session.add(new_record)
             self.session.commit()
             self.refresh_list()
        except Exception as e:
             self.session.rollback()
             messagebox.showerror("Error", f"No se pudo agregar el registro: {e}")

    def delete_record(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Atención", "Selecciona un registro para eliminar.")
            return
        record_id = int(self.listbox.get(selection[0]).split(":")[0])
        try:
            record = self.session.get(ChessRecord, record_id)

            if not record:
                messagebox.showwarning("Atención", "No se encontró el registro.")
                return
            self.session.delete(record)
            self.session.commit()
            self.refresh_list()
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")
    
    def edit_record(self):
       selection = self.listbox.curselection()
       if not selection:
           messagebox.showwarning("Atención", "Selecciona un registro para editar.")
           return
       record_id = int(self.listbox.get(selection[0]).split(":")[0])

       try:
            record = self.session.get(ChessRecord, record_id)
            if not record:
                messagebox.showwarning("Atención", "No se encontró el registro.")
                return

            new_result = simpledialog.askstring(
                "Editar", 
                "Nuevo resultado (Ganada o Perdida):",
                initialvalue=record.result
            )
            if new_result is None:
                 return # Cancelado
            
            new_result = new_result.strip().capitalize()
            if new_result not in ("Ganada", "Perdida"):
                 messagebox.showerror("Error", "Resultado inválido. Usa 'Ganada' o 'Perdida'.")
                 return
            
            record.result = new_result
            self.session.commit()
            self.refresh_list()
       except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"No se pudo editar: {e}")

    def on_close(self):
        try:
            self.session.close()
        finally:
            self.root.destroy()

    def sync_from_chesscom(self):
        username = simpledialog.askstring("Chess.com", "Tu username de Chess.com (exacto):") 
        if not username:
            return  # Cancelado
        
        headers = {
            "User-Agent": "ChessRecordApp/1.0 (contacto: tu_correo@ejemplo.com)"
        }

        try:
            # 1) Obtener Lista de archivos mensuales
            url_archives = f"https://api.chess.com/pub/player/{Com3G3tSome}/games/archives"
              
if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()

