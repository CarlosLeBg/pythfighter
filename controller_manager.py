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
        self.triggers: Dict[str, Dict[str, float]] = {
            trg: {'value': 0.0, 'threshold': 0.1, 'last_feedback': 0.0} 
            for trg in self.TRIGGERS
        }
        self.sticks: Dict[str, Dict[str, float]] = {
            stk: {'value': 0.0, 'deadzone': 0.05, 'last_value': 0.0}
            for stk in self.STICKS
        }

        # Configuration avec valeurs optimisées
        self.config = {
            'stick_sensitivity': 0.05,
            'trigger_threshold': 0.1,
            'update_interval': 0.016,
            'deadzone': 0.9,
            'max_retry_attempts': 3,
            'retry_delay': 0.5
        }

        # Vérification des fonctionnalités disponibles
        self._check_controller_capabilities()
        
        # Initialisation des systèmes
        self._setup_callbacks()
        self._configure_initial_state()

    def _check_controller_capabilities(self):
        """Vérifie les fonctionnalités disponibles sur le contrôleur"""
        self.features = {
            'rumble': False,
            'led': hasattr(self.controller, 'lightbar'),
            'trigger_feedback': hasattr(self.controller, 'set_l2_feedback') and 
                              hasattr(self.controller, 'set_r2_feedback')
        }
        
        logger.info(f"Fonctionnalités disponibles: {self.features}")

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

            # Configuration des triggers
            for trg in self.triggers:
                trg_attr = f'{trg}_analog'
                if hasattr(self.controller, trg_attr):
                    getattr(self.controller, trg_attr).on_change(
                        self._create_trigger_callback(trg)
                    )

            # Configuration des sticks
            for stick in self.sticks:
                stick_attr = f'{stick.replace("_", "_stick_")}'
                if hasattr(self.controller, stick_attr):
                    getattr(self.controller, stick_attr).on_change(
                        self._create_stick_callback(stick)
                    )

            logger.info("Callbacks configurés avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la configuration des callbacks: {str(e)}")
            raise DualSenseError("Échec de la configuration des callbacks") from e

    def _create_button_callback(self, btn):
        def callback(value):
            try:
                prev_value = self.buttons[btn]
                self.buttons[btn] = value
                if prev_value != value:
                    logger.info(f"{self.BUTTONS[btn]} est {'pressé' if value else 'relâché'}")
            except Exception as e:
                logger.error(f"Erreur dans le callback du bouton {btn}: {str(e)}")
        return callback

    def _create_trigger_callback(self, trg):
        def callback(value):
            try:
                if abs(value) >= self.triggers[trg]['threshold']:
                    self.triggers[trg]['value'] = value
                    logger.info(f"{self.TRIGGERS[trg]} valeur: {value:.2f}")
                    
                    if self.features['trigger_feedback']:
                        # Feedback haptique avec gestion d'erreur
                        feedback_force = self._calculate_trigger_feedback(value)
                        self._safe_execute(
                            self.set_trigger_feedback,
                            trg,
                            mode='rigid',
                            force=feedback_force
                        )
            except Exception as e:
                logger.error(f"Erreur dans le callback du trigger {trg}: {str(e)}")
        return callback

    def _calculate_trigger_feedback(self, value: float) -> int:
        """Calcule la force du feedback en fonction de la pression"""
        if value > 0.8:
            return 8
        elif value > 0.5:
            return 5
        return 3

    def _create_stick_callback(self, stick):
        def callback(value):
            try:
                if abs(value) > self.sticks[stick]['deadzone']:
                    self.sticks[stick]['value'] = value
                    adjusted_value = self._apply_stick_curve(value)
                    # Évite le spam de logs en vérifiant le changement significatif
                    if abs(adjusted_value - self.sticks[stick]['last_value']) > 0.1:
                        logger.info(f"{self.STICKS[stick]} valeur: {adjusted_value:.2f}")
                        self.sticks[stick]['last_value'] = adjusted_value
            except Exception as e:
                logger.error(f"Erreur dans le callback du stick {stick}: {str(e)}")
        return callback

    def _apply_stick_curve(self, value: float) -> float:
        """Applique une courbe de réponse non linéaire aux sticks"""
        try:
            # Courbe cubique avec limitation
            curve = (value ** 3) if value > 0 else -((-value) ** 3)
            return max(min(curve, 1.0), -1.0)
        except Exception as e:
            logger.error(f"Erreur lors de l'application de la courbe: {str(e)}")
            return value

    def set_trigger_feedback(self, trigger: str, mode: str = 'rigid', force: int = 5):
        """Configure le feedback haptique des triggers avec vérification"""
        if not self.features['trigger_feedback']:
            logger.warning("Feedback des triggers non disponible")
            return

        if trigger not in self.TRIGGERS:
            logger.error(f"Trigger invalide: {trigger}")
            return

        try:
            force = min(10, max(0, force))
            feedback_func = getattr(self.controller, f'set_{trigger}_feedback', None)
            if feedback_func:
                feedback_func(mode, force)
                logger.debug(f"Feedback configuré: {trigger}, {mode}, {force}")
        except Exception as e:
            logger.error(f"Erreur lors de la configuration du feedback: {str(e)}")

    def set_led(self, r: int, g: int, b: int):
        """Configure la LED avec vérification"""
        if not self.features['led']:
            logger.warning("LED non disponible")
            return

        try:
            r, g, b = map(lambda x: min(255, max(0, x)), (r, g, b))
            self.controller.lightbar.set_color(r, g, b)
            logger.debug(f"LED configurée: RGB({r}, {g}, {b})")
        except Exception as e:
            logger.error(f"Erreur lors de la configuration LED: {str(e)}")

    def manage_controller(self):
        """Gère le contrôleur avec surveillance d'état"""
        logger.info("Démarrage de la gestion du contrôleur")
        last_check = time.time()
        check_interval = 1.0  # Vérification de l'état toutes les secondes

        try:
            while not self.buttons['ps']:
                current_time = time.time()
                
                # Mise à jour périodique de l'état
                if current_time - last_check >= check_interval:
                    self._check_controller_state()
                    last_check = current_time

                # Mise à jour du feedback visuel
                self._update_led_feedback()
                
                time.sleep(self.config['update_interval'])

        except KeyboardInterrupt:
            logger.info("Arrêt demandé par l'utilisateur")
        except Exception as e:
            logger.error(f"Erreur dans la boucle principale: {str(e)}")
        finally:
            self.stop()

    def _check_controller_state(self):
        """Vérifie l'état du contrôleur"""
        try:
            if not self.controller:
                raise DualSenseError("Contrôleur non initialisé")
            # Ajoutez ici d'autres vérifications d'état si nécessaire
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'état: {str(e)}")

    def _update_led_feedback(self):
        """Met à jour la LED en fonction de l'activité"""
        if not self.features['led']:
            return

        try:
            if any(self.buttons.values()):
                self.set_led(125, 125, 125)
            elif any(v['value'] > 0.5 for v in self.triggers.values()):
                self.set_led(255, 0, 0)
            else:
                self.set_led(0, 0, 255)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour LED: {str(e)}")

    def stop(self):
        """Arrête proprement le contrôleur"""
        logger.info("Arrêt du contrôleur...")
        try:
            if self.features['led']:
                self.set_led(0, 0, 0)
            self.controller.deactivate()
            logger.info("Contrôleur arrêté avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt du contrôleur: {str(e)}")

def main():
    """Point d'entrée principal avec gestion d'erreurs"""
    try:
        dualsense = DualSense()
        dualsense.manage_controller()
    except Exception as e:
        logger.critical(f"Erreur critique: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())