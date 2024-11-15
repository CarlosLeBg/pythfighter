from dualsense_controller import DualSenseController
from time import sleep

class DualSense:
    def __init__(self):
        self.controller = DualSenseController()
        self.controller.activate()

        self.L1 = False
        self.R1 = False
        self.L2 = 0
        self.R2 = 0
        self.L3 = False
        self.R3 = False
        self.cross = False
        self.circle = False
        self.square = False
        self.triangle = False
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.options = False
        self.create = False
        self.ps = False
        self.touchpad = False
        
        self.left_stick_x = 0
        self.left_stick_y = 0
        self.right_stick_x = 0
        self.right_stick_y = 0

        self._setup_callbacks()

    def _setup_callbacks(self):
        self.controller.btn_l1.on_change(lambda v: setattr(self, 'L1', v))
        self.controller.btn_r1.on_change(lambda v: setattr(self, 'R1', v))
        self.controller.btn_l3.on_change(lambda v: setattr(self, 'L3', v))
        self.controller.btn_r3.on_change(lambda v: setattr(self, 'R3', v))
        self.controller.btn_cross.on_change(lambda v: setattr(self, 'cross', v))
        self.controller.btn_circle.on_change(lambda v: setattr(self, 'circle', v))
        self.controller.btn_square.on_change(lambda v: setattr(self, 'square', v))
        self.controller.btn_triangle.on_change(lambda v: setattr(self, 'triangle', v))
        self.controller.btn_up.on_change(lambda v: setattr(self, 'up', v))
        self.controller.btn_down.on_change(lambda v: setattr(self, 'down', v))
        self.controller.btn_left.on_change(lambda v: setattr(self, 'left', v))
        self.controller.btn_right.on_change(lambda v: setattr(self, 'right', v))
        self.controller.btn_options.on_change(lambda v: setattr(self, 'options', v))
        self.controller.btn_create.on_change(lambda v: setattr(self, 'create', v))
        self.controller.btn_ps.on_change(lambda v: setattr(self, 'ps', v))
        self.controller.btn_touchpad.on_change(lambda v: setattr(self, 'touchpad', v))

        self.controller.left_trigger.on_change(lambda v: setattr(self, 'L2', v))
        self.controller.right_trigger.on_change(lambda v: setattr(self, 'R2', v))

        self.controller.left_stick_x.on_change(lambda v: setattr(self, 'left_stick_x', v))
        self.controller.left_stick_y.on_change(lambda v: setattr(self, 'left_stick_y', v))
        self.controller.right_stick_x.on_change(lambda v: setattr(self, 'right_stick_x', v))
        self.controller.right_stick_y.on_change(lambda v: setattr(self, 'right_stick_y', v))

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
            if pad.cross:
                pad.rumble(100, 100)
            if pad.L1:
                pad.set_led(255, 0, 0)
            if pad.ps:
                break
            sleep(0.016)
    
    finally:
        pad.stop()