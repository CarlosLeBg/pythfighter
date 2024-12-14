from dualsense_controller import DualSenseController
from time import sleep

class DualSense:
    def __init__(self):
        self.controller = DualSenseController()
        self.controller.activate()

        self.buttons = {
            'L1': False, 'R1': False, 'L3': False, 'R3': False,
            'cross': False, 'circle': False, 'square': False, 'triangle': False,
            'up': False, 'down': False, 'left': False, 'right': False,
            'options': False, 'create': False, 'ps': False, 'touchpad': False
        }

        self.triggers = {'L2': 0, 'R2': 0}
        self.sticks = {'left_x': 0, 'left_y': 0, 'right_x': 0, 'right_y': 0}

        self._setup_callbacks()

    def _setup_callbacks(self):
        for btn in self.buttons:
            getattr(self.controller, f'btn_{btn}').on_change(lambda v, btn=btn: self._update_button(btn, v))

        for trg in self.triggers:
            getattr(self.controller, f'{trg.lower()}').on_change(lambda v, trg=trg: self._update_trigger(trg, v))

        for stick in self.sticks:
            getattr(self.controller, f'{stick.replace("_", "_stick_")}').on_change(
                lambda v, stick=stick: self._update_stick(stick, v)
            )

    def _update_button(self, button, value):
        self.buttons[button] = value

    def _update_trigger(self, trigger, value):
        self.triggers[trigger] = value

    def _update_stick(self, stick, value):
        self.sticks[stick] = value

    def set_led(self, r, g, b):
        self.controller.lightbar.set_color(r, g, b)

    def rumble(self, left=0, right=0):
        self.controller.left_rumble.set(left)
        self.controller.right_rumble.set(right)

    def stop(self):
        self.controller.deactivate()

if __name__ == "__main__":
    pad = DualSense()
    try:
        while True:
            if pad.buttons['cross']:
                pad.rumble(100, 100)
            if pad.buttons['L1']:
                pad.set_led(255, 0, 0)
            if pad.buttons['ps']:
                break
            sleep(0.016)
    finally:
        pad.stop()