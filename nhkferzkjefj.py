import time
from dualsense_controller import DualSenseController

dualsense_controller = DualSenseController()
dualsense_controller.activate()

try:
    while True:
        dualsense_controller.set_haptic(0, 255)  # Vibration maximale sur le moteur gauche
        dualsense_controller.set_haptic(1, 255)  # Vibration maximale sur le moteur droit
        time.sleep(0.5)  # Pause de 0.5 seconde
        dualsense_controller.set_haptic(0, 0)    # Arrêter la vibration sur le moteur gauche
        dualsense_controller.set_haptic(1, 0)    # Arrêter la vibration sur le moteur droit
        time.sleep(0.5)  # Pause de 0.5 seconde
except KeyboardInterrupt:
    dualsense_controller.deactivate()
    print("Vibrations arrêtées et contrôleur désactivé.")