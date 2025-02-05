import tkinter as tk
import os
import sys
import subprocess

class LauncherPythFighter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#1A1A2E')

        self.colors = {
            'background': '#1A1A2E',
            'primary': '#E94560',
            'secondary': '#16213E',
            'text': '#FFFFFF'
        }

        self.canvas = tk.Canvas(
            self.root, 
            bg=self.colors['background'], 
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.creer_interface()
        self.bind_global_keys()

    def creer_interface(self):
        # Titre principal
        self.canvas.create_text(
            self.root.winfo_screenwidth() // 2, 150, 
            text="PYTH FIGHTER", 
            font=("Arial Black", 100), 
            fill=self.colors['primary']
        )

        # Boutons de menu
        menu_items = [
            ("Démarrer", self.lancer_jeu),
            ("Crédits", self.afficher_credits),
            ("Quitter", self.root.quit)
        ]

        for i, (texte, commande) in enumerate(menu_items):
            bouton = tk.Button(
                self.root, 
                text=texte, 
                font=("Arial", 30),
                bg=self.colors['secondary'], 
                fg=self.colors['text'],
                activebackground=self.colors['primary'],
                command=commande
            )
            self.canvas.create_window(
                self.root.winfo_screenwidth() // 2, 
                400 + (i * 100), 
                window=bouton, 
                width=400, 
                height=70
            )

    def bind_global_keys(self):
        self.root.bind('<Return>', lambda e: self.skip_credits())

    def lancer_jeu(self):
        chemin_jeu = os.path.join(os.path.dirname(__file__), "selector.py")
        try:
            subprocess.Popen([sys.executable, chemin_jeu])
            self.root.quit()
        except Exception as e:
            print(f"Erreur de lancement : {e}")

    def afficher_credits(self):
        self.fenetre_credits = tk.Toplevel(self.root)
        self.fenetre_credits.attributes('-fullscreen', True)
        self.fenetre_credits.configure(bg=self.colors['background'])

        # Texte des crédits
        texte_credits = """
        PythFighter - Un jeu de combat révolutionnaire

        Développé avec passion par l'équipe de développement PythFighter

        Programmation : 
        - Développeurs principaux
        - Contributeurs open-source

        Design graphique :
        - Artistes de conception
        - Concepteurs d'interface

        Musique et effets sonores :
        - Compositeurs
        - Ingénieurs du son

        Remerciements spéciaux :
        - Communauté Python
        - Tous les joueurs qui nous soutiennent

        Merci d'avoir choisi PythFighter !
        """

        # Label de défilement des crédits
        self.label_credits = tk.Label(
            self.fenetre_credits, 
            text=texte_credits, 
            font=("Arial", 20), 
            bg=self.colors['background'], 
            fg=self.colors['primary'],
            justify=tk.CENTER
        )
        self.label_credits.place(relx=0.5, rely=1.0, anchor=tk.S)

        # Événements de la fenêtre
        self.fenetre_credits.bind('<Button-1>', self.skip_credits)
        self.fenetre_credits.bind('<Return>', self.skip_credits)

        # Animation de défilement
        self.position_credits = self.root.winfo_screenheight()
        self.animer_credits()

    def animer_credits(self):
        self.position_credits -= 2
        self.label_credits.place(relx=0.5, y=self.position_credits, anchor=tk.S)
        
        if self.position_credits > -self.label_credits.winfo_reqheight():
            self.fenetre_credits.after(50, self.animer_credits)
        else:
            self.fenetre_credits.destroy()

    def skip_credits(self, event=None):
        # Sauter rapidement les crédits
        self.position_credits = -self.label_credits.winfo_reqheight() - 100

    def executer(self):
        self.root.mainloop()

def main():
    launcher = LauncherPythFighter()
    launcher.executer()

if __name__ == "__main__":
    main()