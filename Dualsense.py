from time import sleep

from dualsense_controller import DualSenseController

# liste les appareils disponibles et lève une exception si aucun appareil n'est détecté
device_infos = DualSenseController.enumerate_devices()
if len(device_infos) < 1:
    raise Exception('No DualSense Controller available.')

# qui maintient le programme
is_running = True

# créer une instance, utiliser le premier appareil disponible
controller = DualSenseController()


# active le drapeau de maintien en vie, ce qui arrête la boucle ci-dessous
def stop():
    global is_running
    is_running = False


# callback, lorsque le bouton cross est pressé, ce qui permet d'activer vibration
def on_cross_btn_pressed():
    print('cross button pressed')
    controller.left_rumble.set(255)
    controller.right_rumble.set(255)


# callback, lorsque le bouton croix est relâché, ce qui désactive le vibration
def on_cross_btn_released():
    print('cross button released')
    controller.left_rumble.set(0)
    controller.right_rumble.set(0)


# callback, lorsque le bouton PlayStation est enfoncé
# arret du programme
def on_ps_btn_pressed():
    print('PS button released -> stop')
    stop()


# callback, en cas d'erreur involontaire,
# i.e. déconnecter physiquement le contrôleur pendant le fonctionnement
# arret du programme
def on_error(error):
    print(f'Opps! an error occured: {error}')
    stop()


# enregistrer les boutons callback
controller.btn_cross.on_down(on_cross_btn_pressed)
controller.btn_cross.on_up(on_cross_btn_released)
controller.btn_ps.on_down(on_ps_btn_pressed)

# enregistrer l'erreur callback
controller.on_error(on_error)

# activer/connecter l'appareil
controller.activate()

# démarrer la boucle de maintien en vie, les entrées et les rappels du contrôleur sont gérés dans un second fil d'exécution
while is_running:
    sleep(0.001)

# désactiver/déconnecter le contrôleur
controller.deactivate()