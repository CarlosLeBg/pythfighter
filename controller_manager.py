import warnings
import logging
from dualsense_controller import DualSenseController
import time
from typing import Optional, Dict, Any

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DualSenseError(Exception):
    """Classe personnalisée pour les erreurs liées au DualSense"""
    pass

class DualSense:
    BUTTONS = {
        'cross': 'Bouton Croix',
        'circle': 'Bouton Cercle',
        'square': 'Bouton Carré',
        'triangle': 'Bouton Triangle',
        'l1': 'Bouton L1',
        'r1': 'Bouton R1',
        'l3': 'Bouton L3',
        'r3': 'Bouton R3',
        'up': 'Bouton Haut',
        'down': 'Bouton Bas',
        'left': 'Bouton Gauche',
        'right': 'Bouton Droite',
        'options': 'Bouton Options',
        'create': 'Bouton Create',
        'ps': 'Bouton PS',
        'touchpad': 'Bouton Touchpad'
    }

    TRIGGERS = {
        'l2': 'Trigger L2',
        'r2': 'Trigger R2'
    }

    STICKS = {
        'left_x': 'Stick Gauche X',
        'left_y': 'Stick Gauche Y',
        'right_x': 'Stick Droit X',
        'right_y': 'Stick Droit Y'
    }

    def __init__(self):
        try:
            self.controller = DualSenseController()
            self.controller.activate()
            logger.info("Contrôleur DualSense initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du contrôleur: {str(e)}")
            raise DualSenseError("Impossible d'initialiser le contrôleur") from e

        # État des contrôles avec valeurs par défaut sécurisées
        self.buttons: Dict[str, bool] = {btn: False for btn in self.BUTTONS}
        self.triggers: Dict[str, float] = {trg: 0.0 for trg in self.TRIGGERS}
        self.sticks: Dict[str, float] = {stk: 0.0 for stk in self.STICKS}
        self.stick_locked: Dict[str, bool] = {'left': False, 'right': False}

        # Configuration avec valeurs optimisées
        self.config = {
            'stick_sensitivity': 0.05,
            'trigger_threshold': 0.1,
            'update_interval': 0.016,
            'deadzone': 0.05,
            'max_retry_attempts': 3,
            'retry_delay': 0.5
        }

        # Vérification des fonctionnalités disponibles
        self._check_controller_capabilities()
        
        # Initialisation des systèmes
        self._setup_callbacks()
        self._configure_initial_state()

        self.l2_value = 0.0
        self.r2_value = 0.0
        self._setup_triggers()

    def _check_controller_capabilities(self):
        """Vérifie les fonctionnalités disponibles sur le contrôleur"""
        self.features = {
            'rumble': hasattr(self.controller, 'set_rumble'),
            'led': hasattr(self.controller, 'lightbar'),
            'trigger_feedback': hasattr(self.controller, 'set_l2_feedback') and 
                              hasattr(self.controller, 'set_r2_feedback')
        }

    def _setup_callbacks(self):
        """Configure les callbacks avec gestion d'erreurs"""
        try:
            # Configuration des boutons
            for btn in self.buttons:
                btn_attr = f'btn_{btn}'
                if hasattr(self.controller, btn_attr):
                    getattr(self.controller, btn_attr).on_change(
                        self._create_button_callback(btn)
                    )

            # Configuration des triggers avec effets adaptatifs
            for trg in self.triggers:
                trg_analog_attr = f"{trg}_analog"
                trg_effect_attr = f"{trg}_trigger_effect"

                # Vérifier si le contrôleur a les attributs nécessaires
                if hasattr(self.controller, trg_analog_attr):
                    # Configurer le callback pour les valeurs analogiques
                    getattr(self.controller, trg_analog_attr).on_change(
                        self._create_trigger_callback(trg)
                    )

                # Configurer un effet adaptatif par défaut si disponible
                if hasattr(self.controller, trg_effect_attr):
                    effect = getattr(self.controller, trg_effect_attr)
                    effect.set_mode('rigid')
                    effect.set_force(5)

            # Configuration des sticks
            for stick in self.sticks:
                stick_attr = f'{stick.replace("_", "_stick_")}'
                if hasattr(self.controller, stick_attr):
                    getattr(self.controller, stick_attr).on_change(
                        self._create_stick_callback(stick)
                    )

        except Exception as e:
            logger.error(f"Erreur lors de la configuration des callbacks: {str(e)}")
            raise DualSenseError("Impossible de configurer les callbacks") from e

    def _create_button_callback(self, btn):
        def callback(value):
            self._update_button(btn, value)
        return callback

    def _create_trigger_callback(self, trg):
        def callback(value):
            self._update_trigger(trg, value)
        return callback

    def _create_stick_callback(self, stick):
        def callback(value):
            self._update_stick(stick, value)
        return callback

    def _update_button(self, btn, value):
        self.buttons[btn] = value
        print(f"{self.BUTTONS[btn]} est {'pressé' if value else 'relâché'}")

        # Bloquer les sticks si L3 ou R3 est pressé
        if btn == 'l3':
            self.stick_locked['left'] = value
        elif btn == 'r3':
            self.stick_locked['right'] = value

    def _update_trigger(self, trg, value):
        self.triggers[trg] = value
        print(f"{self.TRIGGERS[trg]} valeur est {value}")

    def _update_stick(self, stick, value):
        stick_side = 'left' if 'left' in stick else 'right'
        if not self.stick_locked[stick_side] and abs(value) > self.config['deadzone']:  # Appliquer la sensibilité
            self.sticks[stick] = value
            print(f"{self.STICKS[stick]} valeur est {value}")

    def _configure_initial_state(self):
        """Configure l'état initial du contrôleur avec gestion d'erreurs"""
        try:
            if self.features['led']:
                self.set_led(0, 0, 255)
            if self.features['trigger_feedback']:
                self._safe_execute(self.set_trigger_feedback, 'l2', mode='rigid', force=5)
                self._safe_execute(self.set_trigger_feedback, 'r2', mode='rigid', force=5)
            
            logger.info("Configuration initiale terminée")
        except Exception as e:
            logger.error(f"Erreur lors de la configuration initiale: {str(e)}")

    def _safe_execute(self, func, *args, **kwargs):
        """Exécute une fonction avec gestion des erreurs et tentatives"""
        for attempt in range(self.config['max_retry_attempts']):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Tentative {attempt + 1} échouée: {str(e)}")
                if attempt + 1 == self.config['max_retry_attempts']:
                    logger.error(f"Échec de l'exécution de {func.__name__}: {str(e)}")
                    return None
                time.sleep(self.config['retry_delay'])

    def set_led(self, r, g, b):
        self.controller.lightbar.set_color(r, g, b)

    def set_trigger_feedback(self, trigger, mode, force):
        if trigger == 'l2':
            self.controller.set_l2_feedback(mode, force)
        elif trigger == 'r2':
            self.controller.set_r2_feedback(mode, force)

    def stop(self):
        self.controller.deactivate()

    def _setup_triggers(self):
        """Configuration des triggers"""
        try:
            # Utiliser les bons attributs pour les triggers
            if hasattr(self.controller, 'left_trigger'):
                self.controller.left_trigger.on_change(self._on_l2_change)
                logger.info("L2 configuré avec succès")
            
            if hasattr(self.controller, 'right_trigger'):
                self.controller.right_trigger.on_change(self._on_r2_change)
                logger.info("R2 configuré avec succès")

        except Exception as e:
            logger.error(f"Erreur configuration triggers: {e}")

    def _on_l2_change(self, value):
        """Callback pour L2"""
        self.l2_value = value
        logger.info(f"L2 value: {value}")
        if value > 0:
            self.controller.left_rumble = int(value * 100)

    def _on_r2_change(self, value):
        """Callback pour R2"""
        self.r2_value = value 
        logger.info(f"R2 value: {value}")
        if value > 0:
            self.controller.right_rumble = int(value * 100)

    def update_triggers(self):
        """Mise à jour manuelle des triggers"""
        try:
            if hasattr(self.controller, 'l2'):
                self.l2_value = self.controller.l2.value
                logger.debug(f"L2 update: {self.l2_value}")

            if hasattr(self.controller, 'r2'):
                self.r2_value = self.controller.r2.value
                logger.debug(f"R2 update: {self.r2_value}")

        except Exception as e:
            logger.error(f"Erreur update triggers: {e}")

    def update(self):
        """Mise à jour des triggers"""
        try:
            if hasattr(self.controller, 'left_trigger'):
                current_l2 = self.controller.left_trigger.value
                if current_l2 != self.l2_value:
                    self._on_l2_change(current_l2)

            if hasattr(self.controller, 'right_trigger'):
                current_r2 = self.controller.right_trigger.value
                if current_r2 != self.r2_value:
                    self._on_r2_change(current_r2)

        except Exception as e:
            logger.error(f"Erreur mise à jour triggers: {e}")

# Exemple d'utilisation
if __name__ == "__main__":
    dualsense = DualSense()
    try:
        print("Contrôleur actif - Appuyez sur les triggers L2/R2")
        while True:
            dualsense.update()  # Mise à jour active des triggers
            time.sleep(0.016)  # ~60Hz
    except KeyboardInterrupt:
        dualsense.stop()
        print("Contrôleur désactivé.")