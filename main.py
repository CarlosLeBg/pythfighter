import tkinter as tk
import os
import subprocess
from tkinter import messagebox

class PythFighterLauncher:
    def __init__(self, master):
        self.master = master
        self.master.title("Launcher du jeu PythFighter")
        self.master.geometry("500x600")
        self.master.configure(bg="#222")
        self.master.minsize(400, 500)

        logo_path = os.path.join(".", "src", "assets", "logo.png")
        self.logo = tk.PhotoImage(file=logo_path).subsample(2, 2)

        self.logo_label = tk.Label(master, image=self.logo, bg="#222")
        self.logo_label.pack(pady=(20, 10))

        self.button_frame = tk.Frame(master, bg="#222")
        self.button_frame.pack(pady=20, padx=20)

        self.launch_button = tk.Button(
            self.button_frame, text="Lancer le jeu", command=self.launch_game,
            font=("Arial", 16, "bold"), bg="#444", fg="white", relief="flat", padx=20, pady=10
        )
        self.launch_button.grid(row=0, column=0, padx=10)

        self.help_button = tk.Button(
            self.button_frame, text="Aide", command=self.show_help,
            font=("Arial", 16, "bold"), bg="#444", fg="white", relief="flat", padx=20, pady=10
        )
        self.help_button.grid(row=0, column=1, padx=10)

        self.launch_button.bind("<Enter>", self.animate_button_in)
        self.launch_button.bind("<Leave>", self.animate_button_out)
        self.help_button.bind("<Enter>", self.animate_button_in)
        self.help_button.bind("<Leave>", self.animate_button_out)

        self.status_var = tk.StringVar(value="Prêt à lancer le jeu.")
        self.status_label = tk.Label(master, textvariable=self.status_var, font=("Arial", 12), bg="#222", fg="white")
        self.status_label.pack(pady=20)

        self.master.protocol("WM_DELETE_WINDOW", self.confirm_exit)

    def launch_game(self):
        self.status_var.set("Lancement du jeu...")
        self.launch_button.config(state=tk.DISABLED)  # Désactive le bouton lors du lancement
        self.master.after(100, self._run_game)

    def _run_game(self):
        try:
            subprocess.run(["python", "./pythfighter/main.py"], check=True)
            self.status_var.set("Jeu lancé avec succès!")
        except subprocess.CalledProcessError as e:
            self.status_var.set(f"Erreur lors du lancement : {e}")
        except Exception as e:
            self.status_var.set(f"Erreur inconnue : {e}")
        finally:
            self.launch_button.config(state=tk.NORMAL)  # Réactive le bouton après le lancement

    def show_help(self):
        help_text = (
            "PythFighter Launcher\n\n"
            "Utilisez ce launcher pour lancer le jeu PythFighter.\n"
            "Cliquez sur 'Lancer le jeu' pour démarrer.\n"
            "Si vous avez besoin d'aide supplémentaire, consultez la documentation du jeu."
        )
        messagebox.showinfo("Aide", help_text)

    def confirm_exit(self):
        if messagebox.askyesno("Quitter", "Êtes-vous sûr de vouloir quitter ?"):
            self.master.quit()

    def animate_button_in(self, event):
        event.widget.config(bg="#666", relief="raised", highlightbackground="#555")
        event.widget['font'] = ("Arial", 18, "bold")

    def animate_button_out(self, event):
        event.widget.config(bg="#444", relief="flat")
        event.widget['font'] = ("Arial", 16, "bold")

if __name__ == "__main__":
    root = tk.Tk()
    app = PythFighterLauncher(root)
    root.mainloop()
