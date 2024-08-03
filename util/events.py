
import random

from ppadb.device import Device as AdbDevice

from .constant import RUNE_SIZE, SCREEN_WIDTH
from .utils import get_grid_loc

"""-----------------send event constant and functions-----------------"""

# suitable for Asus Zenfone M2
EV_SYN = 0
EV_KEY = 1
EV_ABS = 3

SYN_REPORT = 0
ABS_MT_POSITION_X = 53
ABS_MT_POSITION_Y = 54
ABS_MT_TRACKING_ID = 57
BTN_TOUCH = 330

DEV = '/dev/input/event1'

# for ld player
ABS_MT_TRACKING_ID = 58
DEV = '/dev/input/event2'

def sendevent(device: AdbDevice,type: int, code: int, value: int, dev: str=DEV):
    device.shell(f'sendevent {dev} {type} {code} {value}')

def send_SYN_REPORT(device: AdbDevice, dev: str=DEV) -> None:
    sendevent(device, EV_SYN, SYN_REPORT, 0, dev)

def send_BTN_TOUCH_DOWN(device: AdbDevice, dev: str=DEV) -> None:
    sendevent(device, EV_KEY, BTN_TOUCH, 1, dev)

def send_POSITION(device: AdbDevice, x: int, y: int, dev: str=DEV) -> None:
    sendevent(device, EV_ABS, ABS_MT_POSITION_X, x, dev)
    sendevent(device, EV_ABS, ABS_MT_POSITION_Y, y, dev)
    send_SYN_REPORT(device, dev)

def send_ABS_MT_TRACKING_ID(device: AdbDevice, x: int, dev: str=DEV) -> None:
    sendevent(device, EV_ABS, ABS_MT_TRACKING_ID, x, dev)



"""-----------------send event functions-----------------"""

def route_move(device: AdbDevice, route: list[tuple[int, int]]) -> None:
    route_loc = [get_grid_loc(x, y) for x, y in route]
    tolerance = RUNE_SIZE // 4
    dx, dy = random.randint(-tolerance, tolerance), random.randint(-tolerance, tolerance)
    route_loc = [(x + RUNE_SIZE // 2 + dx, y + RUNE_SIZE // 2 + dy) for x, y in route_loc]
    route_loc = [(y, SCREEN_WIDTH - x) for x, y in route_loc] # weird coordinate system of ld player

    send_ABS_MT_TRACKING_ID(device, 1)
    sendevent(device, EV_KEY, BTN_TOUCH, 1)

    for x, y in route_loc:
        send_POSITION(device, x, y)

    send_ABS_MT_TRACKING_ID(device, -1)
    sendevent(device, EV_KEY, BTN_TOUCH, 0)
    send_SYN_REPORT(device)