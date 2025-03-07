import tkinter as tk
from tkinter import messagebox, ttk
import os
import sys
import subprocess
from typing import Tuple, List, Callable, Dict
import math
import random
import logging

class LauncherPythFighter:
    """Launcher principal pour le jeu PythFighter avec un design premium et gestion d'erreurs."""
    
    COLORS: Dict[str, str] = {
        'background': '#0A0A1A',
        'primary': '#FF3366',
        'secondary': '#1A1A2E',
        'accent': '#00FFFF',
        'text': '#FFFFFF',
        'text_secondary': '#AAAAAA',
        'button_hover': '#FF6B9B',
        'button_active': '#FF1A4D',
        'shadow': '#070711'
    }

    FONTS: Dict[str, tuple] = {
        'title': ("Helvetica", 100, "bold"),
        'subtitle': ("Helvetica", 28),
        'button': ("Helvetica", 18, "bold"),
        'credits': ("Helvetica", 16),
        'version': ("Helvetica", 14)
    }

    def __init__(self) -> None:
        """Initialisation avec gestion d'erreurs."""
        try:
            # Configuration du logging
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s',
                filename='launcher.log'
            )
            
            self.root = tk.Tk()
            self.screen_width = self.root.winfo_screenwidth()
            self.screen_height = self.root.winfo_screenheight()
            
            # Initialisation des composants dans le bon ordre
            self.setup_window()
            self.setup_canvas()
            self.setup_particles()
            self.create_interface()
            self.setup_animations()
            self.setup_bindings()
            
            logging.info("Launcher initialized successfully")
            
        except Exception as e:
            logging.error(f"Error during initialization: {str(e)}")
            messagebox.showerror("Error", f"Failed to initialize launcher: {str(e)}")
            sys.exit(1)

    def setup_window(self) -> None:
        """Configure la fenêtre principale."""
        try:
            self.root.title("PythFighter Launcher")
            self.root.attributes('-fullscreen', True)
            self.root.configure(bg=self.COLORS['background'])
            
            # Style personnalisé pour les widgets
            self.style = ttk.Style()
            self.style.configure(
                'Custom.TButton',
                background=self.COLORS['secondary'],
                foreground=self.COLORS['text'],
                font=self.FONTS['button'],
                padding=20
            )
            
        except Exception as e:
            logging.error(f"Error setting up window: {str(e)}")
            raise

    def setup_canvas(self) -> None:
        """Crée et configure le canvas principal."""
        try:
            self.canvas = tk.Canvas(
                self.root,
                bg=self.COLORS['background'],
                width=self.screen_width,
                height=self.screen_height,
                highlightthickness=0
            )
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            logging.error(f"Error setting up canvas: {str(e)}")
            raise

    def setup_particles(self) -> None:
        """Initialise les particules d'arrière-plan."""
        try:
            self.particles = []
            for _ in range(50):
                self.particles.append({
                    'x': random.random() * self.screen_width,
                    'y': random.random() * self.screen_height,
                    'size': random.randint(2, 5),
                    'speed': random.random() * 2 + 0.5,
                    'alpha': random.random()  # Pour l'effet de scintillement
                })
            
        except Exception as e:
            logging.error(f"Error setting up particles: {str(e)}")
            raise

    def create_interface(self) -> None:
        """Crée tous les éléments de l'interface."""
        try:
            self._create_background()
            self._create_title()
            self._create_menu_buttons()
            self._create_version_info()
            self._create_decorative_elements()
            
        except Exception as e:
            logging.error(f"Error creating interface: {str(e)}")
            raise

    def _create_background(self) -> None:
        """Crée un arrière-plan avec gradient amélioré."""
        try:
            # Gradient vertical principal
            gradient_steps = 100
            for i in range(gradient_steps):
                y = i * self.screen_height / gradient_steps
                color = self._interpolate_color(
                    self.COLORS['background'],
                    self.COLORS['secondary'],
                    i / gradient_steps
                )
                self.canvas.create_line(
                    0, y, self.screen_width, y,
                    fill=color,
                    width=2
                )
                
            # Ajout d'un effet de vignette
            self._create_vignette()
            
        except Exception as e:
            logging.error(f"Error creating background: {str(e)}")
            raise

    def _create_vignette(self) -> None:
        """Crée un effet de vignette sur les bords."""
        try:
            vignette_size = 100
            for i in range(vignette_size):
                alpha = i / vignette_size
                color = self._interpolate_color(
                    self.COLORS['background'],
                    '#000000',
                    alpha
                )
                # Bords horizontaux
                self.canvas.create_line(
                    0, i,
                    self.screen_width, i,
                    fill=color
                )
                self.canvas.create_line(
                    0, self.screen_height - i,
                    self.screen_width, self.screen_height - i,
                    fill=color
                )
                # Bords verticaux
                self.canvas.create_line(
                    i, 0,
                    i, self.screen_height,
                    fill=color
                )
                self.canvas.create_line(
                    self.screen_width - i, 0,
                    self.screen_width - i, self.screen_height,
                    fill=color
                )
                
        except Exception as e:
            logging.error(f"Error creating vignette: {str(e)}")
            raise

    def _create_title(self) -> None:
        """Crée le titre avec des effets visuels améliorés."""
        try:
            title_y = self.screen_height * 0.2
            
            # Effet de lueur amélioré
            glow_layers = 5
            for i in range(glow_layers):
                offset = (glow_layers - i)
                alpha = (i + 1) / glow_layers
                color = self._interpolate_color(
                    self.COLORS['primary'],
                    self.COLORS['accent'],
                    alpha
                )
                
                # PYTH avec ombre portée
                self.canvas.create_text(
                    self.screen_width // 2 + offset,
                    title_y + offset,
                    text="PYTH",
                    font=self.FONTS['title'],
                    fill=color
                )
                
                # FIGHTER avec ombre portée
                self.canvas.create_text(
                    self.screen_width // 2 + offset,
                    title_y + self.FONTS['title'][1] * 0.8 + offset,
                    text="FIGHTER",
                    font=self.FONTS['title'],
                    fill=color
                )

            # Texte principal
            self._create_main_title_text(title_y)
            
        except Exception as e:
            logging.error(f"Error creating title: {str(e)}")
            raise

    def _create_main_title_text(self, title_y: float) -> None:
        """Crée le texte principal du titre."""
        try:
            # PYTH
            self.canvas.create_text(
                self.screen_width // 2,
                title_y,
                text="PYTH",
                font=self.FONTS['title'],
                fill=self.COLORS['primary']
            )
            
            # FIGHTER
            self.canvas.create_text(
                self.screen_width // 2,
                title_y + self.FONTS['title'][1] * 0.8,
                text="FIGHTER",
                font=self.FONTS['title'],
                fill=self.COLORS['primary']
            )
            
            # Sous-titre animé
            self.subtitle = self.canvas.create_text(
                self.screen_width // 2,
                title_y + self.FONTS['title'][1] * 1.6,
                text="ENTREZ DANS L'ARÈNE",
                font=self.FONTS['subtitle'],
                fill=self.COLORS['accent']
            )
            
        except Exception as e:
            logging.error(f"Error creating main title text: {str(e)}")
            raise

    def _create_menu_buttons(self) -> None:
        """Crée les boutons du menu avec une meilleure disposition."""
        try:
            menu_items = [
                ("DÉMARRER", self.launch_game),
                ("CRÉDITS", self.show_credits),
                ("OPTIONS", self.show_options),
                ("QUITTER", self.confirm_quit)
            ]

            button_frame = tk.Frame(
                self.root,
                bg=self.COLORS['background']
            )
            
            # Position optimisée des boutons
            self.canvas.create_window(
                self.screen_width // 2,
                self.screen_height * 0.55,  # Légèrement plus bas
                window=button_frame
            )

            for i, (text, command) in enumerate(menu_items):
                button = self._create_custom_button(
                    button_frame,
                    text,
                    command
                )
                button.grid(
                    row=i,
                    column=0,
                    pady=20,
                    padx=40
                )
                
        except Exception as e:
            logging.error(f"Error creating menu buttons: {str(e)}")
            raise

    
    def show_credits(self) -> None:
        """Affiche les crédits avec une animation fluide."""
        try:
            self.credits_window = tk.Toplevel(self.root)
            self.credits_window.title("Crédits")
            self.credits_window.attributes('-fullscreen', True)
            self.credits_window.configure(bg=self.COLORS['background'])
            
            # Canvas pour les crédits
            credits_canvas = tk.Canvas(
                self.credits_window,
                bg=self.COLORS['background'],
                highlightthickness=0,
                width=self.screen_width,
                height=self.screen_height
            )
            credits_canvas.pack(fill=tk.BOTH, expand=True)
            
            # Texte des crédits
            credits_text = self._get_credits_text()
            
            # Label des crédits
            self.credits_label = credits_canvas.create_text(
                self.screen_width // 2,
                self.screen_height + 200,  # Commence hors écran
                text=credits_text,
                font=self.FONTS['credits'],
                fill=self.COLORS['primary'],
                justify=tk.CENTER,
                width=self.screen_width * 0.8  # Largeur maximale du texte
            )
            
            # Bouton de fermeture
            close_button = tk.Button(
                self.credits_window,
                text="×",
                font=("Arial", 24, "bold"),
                command=self.close_credits,
                bg=self.COLORS['primary'],
                fg=self.COLORS['text'],
                relief=tk.FLAT,
                cursor="hand2"
            )
            close_button.place(x=20, y=20)
            
            # Bind Escape pour fermer
            self.credits_window.bind("<Escape>", lambda e: self.close_credits())
            
            # Démarrer l'animation
            self.credits_scroll_pos = self.screen_height + 200
            self.credits_canvas = credits_canvas
            self._animate_credits()
            
            logging.info("Credits window opened successfully")
            
        except Exception as e:
            logging.error(f"Error showing credits: {str(e)}")
            if hasattr(self, 'credits_window'):
                self.credits_window.destroy()
            messagebox.showerror("Erreur", "Impossible d'afficher les crédits")

    def _get_credits_text(self) -> str:
        """Retourne le texte des crédits avec mise en forme améliorée."""
        return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        PYTHFIGHTER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Un jeu de combat révolutionnaire

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ÉQUIPE DE DÉVELOPPEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Direction du Projet
------------------
Lead Developer: [Nom]
Project Manager: [Nom]

Programmation
------------
Core Engine: [Nom]
Combat System: [Nom]
UI/UX: [Nom]
Physics Engine: [Nom]

Design
------
Direction Artistique: [Nom]
Character Design: [Nom]
Environment Art: [Nom]
VFX Artist: [Nom]

Audio
-----
Composition Musicale: [Nom]
Sound Design: [Nom]
Voice Acting: [Nom]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    REMERCIEMENTS SPÉCIAUX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Testeurs
--------
[Liste des testeurs]

Contributeurs
------------
[Liste des contributeurs]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    TECHNOLOGIES UTILISÉES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Python
Tkinter
[Autres technologies]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Copyright © 2024 PythFighter
Tous droits réservés

Version 1.0.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    def _animate_credits(self) -> None:
        """Anime le défilement des crédits avec une vitesse et accélération contrôlées."""
        try:
            # Vitesse de défilement variable
            scroll_speed = 1.5
            
            # Mise à jour de la position
            self.credits_scroll_pos -= scroll_speed
            self.credits_canvas.coords(
                self.credits_label,
                self.screen_width // 2,
                self.credits_scroll_pos
            )
            
            # Vérifier si l'animation doit continuer
            credits_bbox = self.credits_canvas.bbox(self.credits_label)
            if credits_bbox and credits_bbox[3] > 0:  # Si le texte est encore visible
                self.credits_window.after(20, self._animate_credits)
            else:
                # Redémarrer l'animation
                self.credits_scroll_pos = self.screen_height + 200
                self._animate_credits()
                
        except Exception as e:
            logging.error(f"Error animating credits: {str(e)}")
            self.close_credits()

    def close_credits(self) -> None:
        """Ferme proprement la fenêtre des crédits."""
        try:
            if hasattr(self, 'credits_window') and self.credits_window is not None:
                self.credits_window.destroy()
                self.credits_window = None
                logging.info("Credits window closed successfully")
                
        except Exception as e:
            logging.error(f"Error closing credits: {str(e)}")

    def show_options(self) -> None:
        """Affiche et gère le menu des options."""
        try:
            self.options_window = tk.Toplevel(self.root)
            self.options_window.title("Options")
            
            # Centrer la fenêtre
            window_width = 500
            window_height = 600
            x = (self.screen_width - window_width) // 2
            y = (self.screen_height - window_height) // 2
            self.options_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            self.options_window.configure(bg=self.COLORS['background'])
            self.options_window.resizable(False, False)
            
            # Titre
            title_label = tk.Label(
                self.options_window,
                text="OPTIONS",
                font=self.FONTS['subtitle'],
                bg=self.COLORS['background'],
                fg=self.COLORS['primary']
            )
            title_label.pack(pady=20)
            
            # Frame principal pour les options
            options_frame = tk.Frame(
                self.options_window,
                bg=self.COLORS['background']
            )
            options_frame.pack(fill=tk.BOTH, expand=True, padx=40)
            
            # Options de jeu
            self._create_options_section(options_frame, "PARAMÈTRES DE JEU", [
                ("Plein écran", True),
                ("VSync", True),
                ("Afficher FPS", False)
            ])
            
            # Options audio
            self._create_options_section(options_frame, "AUDIO", [
                ("Musique", True),
                ("Effets sonores", True),
                ("Voix", True)
            ])
            
            # Options graphiques
            self._create_options_section(options_frame, "GRAPHIQUES", [
                ("Qualité élevée", True),
                ("Effets visuels", True),
                ("Ombres", True)
            ])
            
            # Options de contrôle
            self._create_options_section(options_frame, "CONTRÔLES", [
                ("Vibrations", True),
                ("Aide à la visée", False),
                ("Inversion Y", False)
            ])
            
            # Boutons de confirmation
            self._create_option_buttons()
            
            # Bind Escape pour fermer
            self.options_window.bind("<Escape>", lambda e: self.close_options())
            
            # Rendre la fenêtre modale
            self.options_window.transient(self.root)
            self.options_window.grab_set()
            
            logging.info("Options window opened successfully")
            
        except Exception as e:
            logging.error(f"Error showing options: {str(e)}")
            if hasattr(self, 'options_window'):
                self.options_window.destroy()
            messagebox.showerror("Erreur", "Impossible d'afficher les options")

    def _create_options_section(self, parent: tk.Frame, title: str, options: List[Tuple[str, bool]]) -> None:
        """Crée une section d'options avec titre et switches."""
        try:
            # Frame pour la section
            section_frame = tk.Frame(
                parent,
                bg=self.COLORS['background']
            )
            section_frame.pack(fill=tk.X, pady=10)
            
            # Titre de la section
            section_title = tk.Label(
                section_frame,
                text=title,
                font=self.FONTS['button'],
                bg=self.COLORS['background'],
                fg=self.COLORS['accent']
            )
            section_title.pack(anchor='w', pady=(10, 5))
            
            # Ligne de séparation
            separator = ttk.Separator(section_frame, orient='horizontal')
            separator.pack(fill=tk.X, pady=5)
            
            # Options
            for option_text, default_value in options:
                option_var = tk.BooleanVar(value=default_value)
                self._create_option_row(section_frame, option_text, option_var)
                
        except Exception as e:
            logging.error(f"Error creating options section: {str(e)}")
            raise

    def _create_option_row(self, parent: tk.Frame, text: str, var: tk.BooleanVar) -> None:
        """Crée une ligne d'option avec texte et switch."""
        try:
            row_frame = tk.Frame(
                parent,
                bg=self.COLORS['background']
            )
            row_frame.pack(fill=tk.X, pady=5)
            
            # Label
            label = tk.Label(
                row_frame,
                text=text,
                font=("Helvetica", 12),
                bg=self.COLORS['background'],
                fg=self.COLORS['text']
            )
            label.pack(side=tk.LEFT, padx=20)
            
            # Switch personnalisé
            switch = self._create_custom_switch(row_frame, var)
            switch.pack(side=tk.RIGHT, padx=20)
            
        except Exception as e:
            logging.error(f"Error creating option row: {str(e)}")
            raise

    def _create_custom_button(self, parent: tk.Frame, text: str, command: Callable) -> ttk.Button:
        """Crée un bouton personnalisé avec des effets de survol."""
        try:
            button = ttk.Button(
                parent,
                text=text,
                command=command,
                style='Custom.TButton'
            )
            self._add_button_hover_effects(button)
            return button
        except Exception as e:
            logging.error(f"Error creating custom button: {str(e)}")
            raise

    def _create_custom_switch(self, parent: tk.Frame, var: tk.BooleanVar) -> tk.Canvas:
        """Crée un switch personnalisé et animé."""
        try:
            width = 60
            height = 30
            
            switch = tk.Canvas(
                parent,
                width=width,
                height=height,
                bg=self.COLORS['background'],
                highlightthickness=0
            )
            
            # Dessiner le switch
            def update_switch():
                switch.delete("all")
                bg_color = self.COLORS['accent'] if var.get() else self.COLORS['secondary']
                circle_x = width - 20 if var.get() else 20
                
                # Fond
                switch.create_rounded_rect(5, 5, width-5, height-5, 15, fill=bg_color)
                # Cercle
                switch.create_oval(
                    circle_x - 10, 5,
                    circle_x + 10, height-5,
                    fill=self.COLORS['text']
                )
            
            def toggle(event=None):
                var.set(not var.get())
                update_switch()
            
            switch.bind("<Button-1>", toggle)
            update_switch()
            
            return switch
            
        except Exception as e:
            logging.error(f"Error creating custom switch: {str(e)}")
            raise
    def confirm_quit(self) -> None:
        """Affiche une boîte de dialogue de confirmation avant de quitter."""
        try:
            # Créer une fenêtre de dialogue personnalisée
            self.quit_dialog = tk.Toplevel(self.root)
            self.quit_dialog.title("Quitter")
            
            # Centrer la fenêtre
            dialog_width = 400
            dialog_height = 200
            x = (self.screen_width - dialog_width) // 2
            y = (self.screen_height - dialog_height) // 2
            self.quit_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
            
            # Configuration de la fenêtre
            self.quit_dialog.configure(bg=self.COLORS['background'])
            self.quit_dialog.resizable(False, False)
            self.quit_dialog.transient(self.root)
            self.quit_dialog.grab_set()
            
            # Icône d'avertissement
            warning_label = tk.Label(
                self.quit_dialog,
                text="⚠",
                font=("Helvetica", 48),
                bg=self.COLORS['background'],
                fg=self.COLORS['primary']
            )
            warning_label.pack(pady=(20, 10))
            
            # Message
            message_label = tk.Label(
                self.quit_dialog,
                text="Voulez-vous vraiment quitter PythFighter ?",
                font=self.FONTS['button'],
                bg=self.COLORS['background'],
                fg=self.COLORS['text']
            )
            message_label.pack(pady=10)
            
            # Frame pour les boutons
            button_frame = tk.Frame(
                self.quit_dialog,
                bg=self.COLORS['background']
            )
            button_frame.pack(pady=20)
            
            # Bouton Quitter
            quit_button = tk.Button(
                button_frame,
                text="Quitter",
                font=self.FONTS['button'],
                bg=self.COLORS['primary'],
                fg=self.COLORS['text'],
                command=self._quit_application,
                width=10,
                relief=tk.FLAT,
                cursor="hand2"
            )
            quit_button.pack(side=tk.LEFT, padx=10)
            
            # Bouton Annuler
            cancel_button = tk.Button(
                button_frame,
                text="Annuler",
                font=self.FONTS['button'],
                bg=self.COLORS['secondary'],
                fg=self.COLORS['text'],
                command=self._cancel_quit,
                width=10,
                relief=tk.FLAT,
                cursor="hand2"
            )
            cancel_button.pack(side=tk.LEFT, padx=10)
            
            # Ajout des effets de survol
            for button in (quit_button, cancel_button):
                self._add_button_hover_effects(button)
            
            # Bind touches clavier
            self.quit_dialog.bind("<Escape>", lambda e: self._cancel_quit())
            self.quit_dialog.bind("<Return>", lambda e: self._quit_application())
            
            logging.info("Quit confirmation dialog shown")
            
        except Exception as e:
            logging.error(f"Error showing quit confirmation: {str(e)}")
            self._quit_application()  # Quitter directement en cas d'erreur

    def _add_button_hover_effects(self, button: tk.Button) -> None:
        """Ajoute des effets de survol aux boutons."""
        try:
            original_bg = button.cget("bg")
            hover_bg = self.COLORS['button_hover'] if original_bg == self.COLORS['primary'] else self.COLORS['button_active']
            
            def on_enter(e):
                button.config(bg=hover_bg)
            
            def on_leave(e):
                button.config(bg=original_bg)
            
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
            
        except Exception as e:
            logging.error(f"Error adding button hover effects: {str(e)}")

    def _cancel_quit(self) -> None:
        """Annule la fermeture de l'application."""
        try:
            if hasattr(self, 'quit_dialog') and self.quit_dialog is not None:
                self.quit_dialog.destroy()
                self.quit_dialog = None
                logging.info("Quit cancelled")
                
        except Exception as e:
            logging.error(f"Error cancelling quit: {str(e)}")

    def _quit_application(self) -> None:
        """Ferme proprement l'application."""
        try:
            logging.info("Application shutting down")
            self.root.quit()
            
        except Exception as e:
            logging.error(f"Error during application shutdown: {str(e)}")
            sys.exit(1)  # Forcer la fermeture en cas d'erreur

    def _create_option_buttons(self) -> None:
        """Crée les boutons de confirmation et d'annulation."""
        try:
            button_frame = tk.Frame(
            self.options_window,
            bg=self.COLORS['background']
            )
            button_frame.pack(pady=20, padx=40, fill=tk.X)
            
            # Bouton Appliquer
            apply_button = tk.Button(
            button_frame,
            text="Appliquer",
            font=self.FONTS['button'],
            bg=self.COLORS['primary'],
            fg=self.COLORS['text'],
            command=self.apply_options,
            relief=tk.FLAT,
            cursor="hand2"
            )
            apply_button.pack(side=tk.RIGHT, padx=5)
            
            # Bouton Annuler
            cancel_button = tk.Button(
            button_frame,
            text="Annuler",
            font=self.FONTS['button'],
            bg=self.COLORS['secondary'],
            fg=self.COLORS['text'],
            command=self.close_options,
            relief=tk.FLAT,
            cursor="hand2"
            )
            cancel_button.pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            logging.error(f"Error creating option buttons: {str(e)}")
            raise

    def apply_options(self) -> None:
        """Applique les options sélectionnées."""
        try:
            # TODO: Sauvegarder les options
            messagebox.showinfo("Succès", "Options appliquées avec succès!")
            self.close_options()
            
        except Exception as e:
            logging.error(f"Error applying options: {str(e)}")
            messagebox.showerror("Erreur", "Impossible d'appliquer les options")

    def close_options(self) -> None:
        """Ferme la fenêtre des options."""
        try:
            if hasattr(self, 'options_window') and self.options_window is not None:
                self.options_window.destroy()
                self.options_window = None
                logging.info("Options window closed successfully")
                
        except Exception as e:
            logging.error(f"Error closing options: {str(e)}")

    def setup_animations(self) -> None:
        """Configure toutes les animations."""
        try:
            self._animate_particles()
            self._animate_subtitle()
            
        except Exception as e:
            logging.error(f"Error setting up animations: {str(e)}")
            raise

    def setup_bindings(self) -> None:
        """Configure tous les événements clavier."""
        try:
            self.root.bind("<Escape>", lambda e: self.confirm_quit())
            self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
            
        except Exception as e:
            logging.error(f"Error setting up key bindings: {str(e)}")
            raise

    def toggle_fullscreen(self) -> None:
        """Bascule entre mode plein écran et fenêtré."""
        try:
            is_fullscreen = self.root.attributes('-fullscreen')
            self.root.attributes('-fullscreen', not is_fullscreen)
            
        except Exception as e:
            logging.error(f"Error toggling fullscreen: {str(e)}")

    def _interpolate_color(self, color1: str, color2: str, factor: float) -> str:
        """Interpole entre deux couleurs hexadécimales."""
        try:
            r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
            r = int(r1 + (r2 - r1) * factor)
            g = int(g1 + (g2 - g1) * factor)
            b = int(b1 + (b2 - b1) * factor)
            return f'#{r:02x}{g:02x}{b:02x}'
            
        except Exception as e:
            logging.error(f"Error interpolating colors: {str(e)}")
            return color1

    def launch_game(self) -> None:
        """Lance le jeu avec gestion d'erreurs améliorée."""
        try:
            game_path = os.path.join(os.path.dirname(__file__), "selector.py")
            if not os.path.exists(game_path):
                raise FileNotFoundError(f"Game file not found: {game_path}")
                
            subprocess.Popen([sys.executable, game_path])
            self.root.quit()
            
        except Exception as e:
            logging.error(f"Error launching game: {str(e)}")
            messagebox.showerror(
                "Erreur de lancement",
                f"Impossible de lancer le jeu:\n{str(e)}"
            )

    def run(self) -> None:
        """Lance le launcher avec gestion d'erreurs."""
        try:
            self.root.mainloop()
            
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            sys.exit(1)

def main():
    try:
        launcher = LauncherPythFighter()
        launcher.run()
        
    except Exception as e:
        logging.error(f"Fatal error in main: {str(e)}")
        messagebox.showerror("Fatal Error", f"Cannot start launcher: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()