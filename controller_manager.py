from time import sleep
from dualsense_controller import DualSenseController

def list_devices():
    devices = DualSenseController.enumerate_devices()
    if not devices:
        raise Exception('No DualSense Controller available.')
    return devices

def activate_controller():
    controller = DualSenseController()
    controller.activate()
    return controller

def stop_controller(controller):
    controller.deactivate()

controller = activate_controller()

controller.btn_cross.on_down(lambda: controller.rumble(255, 255))
controller.btn_cross.on_up(lambda: controller.rumble(0, 0))
controller.btn_ps.on_down(lambda: stop_controller(controller))

try:
    while True:
        sleep(0.001)
except KeyboardInterrupt:
    stop_controller(controller)
