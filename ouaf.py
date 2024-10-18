import pyautogui
import time

def autoclicker(interval, duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        pyautogui.click()
        time.sleep(interval)

# Intervalle entre les clics en secondes (par exemple, 0.1 secondes)
interval = 0.1
# Durée pendant laquelle l'autoclicker doit fonctionner (par exemple, 10 secondes)
duration = 10

autoclicker(interval, duration)
