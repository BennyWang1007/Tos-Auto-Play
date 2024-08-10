import os
import random
from typing import Literal

from ppadb.device import Device as AdbDevice

from .constant import RUNE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, ROW_NUM, COL_NUM
from .utils import get_grid_loc, get_adb_device

"""-----------------send event constant and functions-----------------"""

# suitable for Asus Zenfone M2
EV_SYN = 0
EV_KEY = 1
EV_ABS = 3

SYN_REPORT = 0
SYN_MT_REPORT = 2
ABS_MT_POSITION_X = 53
ABS_MT_POSITION_Y = 54
ABS_MT_TRACKING_ID = 57
BTN_TOUCH = 330

DEV = '/dev/input/event1'

ANDROID_DEVICE: Literal["LdPlayer", "BlueStack", "Nox", "Else"] = "Nox"

# ANDROID_DEVICE = "LdPlayer"

# for ld player
if ANDROID_DEVICE == "LdPlayer":
    ABS_MT_TRACKING_ID = 58
    DEV = '/dev/input/event2'

# for bluestacks
if ANDROID_DEVICE == "BlueStack":
    DEV = '/dev/input/event5'

if ANDROID_DEVICE == "Nox":
    DEV = '/dev/input/event4'


def sendevent(device: AdbDevice, type: int, code: int, value: int, dev: str=DEV):
    device.shell(f'sendevent {dev} {type} {code} {value}')

def send_SYN_REPORT(device: AdbDevice, dev: str=DEV) -> None:
    sendevent(device, EV_SYN, SYN_REPORT, 0, dev)

def send_BTN_TOUCH_DOWN(device: AdbDevice, dev: str=DEV) -> None:
    sendevent(device, EV_KEY, BTN_TOUCH, 1, dev)

def send_BTN_TOUCH_UP(device: AdbDevice, dev: str=DEV) -> None:
    sendevent(device, EV_KEY, BTN_TOUCH, 0, dev)

def send_POSITION(device: AdbDevice, x: int, y: int, dev: str=DEV, last: bool=False) -> None:
    sendevent(device, EV_ABS, ABS_MT_POSITION_X, x, dev)
    sendevent(device, EV_ABS, ABS_MT_POSITION_Y, y, dev)
    send_SYN_REPORT(device, dev)

def send_ABS_MT_TRACKING_ID(device: AdbDevice, x: int, dev: str=DEV) -> None:
    sendevent(device, EV_ABS, ABS_MT_TRACKING_ID, x, dev)



"""-----------------send event functions-----------------"""

def route_move(device: AdbDevice, route: list[tuple[int, int]]) -> None:

    tolerance = RUNE_SIZE // 5
    def rand_loc():
        return random.randint(-tolerance, tolerance)
    
    route_loc = [get_grid_loc(x, y) for x, y in route]
    route_loc = [(x + RUNE_SIZE // 2 + rand_loc(), y + RUNE_SIZE // 2 + rand_loc()) for x, y in route_loc]

    # weird coordinate system of emulators
    if ANDROID_DEVICE == "LdPlayer":
        route_loc = [(y, SCREEN_WIDTH - x) for x, y in route_loc]
    elif ANDROID_DEVICE == "BlueStack":
        route_loc = [(SCREEN_HEIGHT - y, x) for x, y in route_loc]
        route_loc = [(int(float(x) / SCREEN_HEIGHT * 32768), int(float(y) / SCREEN_WIDTH * 32768)) for x, y in route_loc]

        
    send_ABS_MT_TRACKING_ID(device, 1)
    send_BTN_TOUCH_DOWN(device)

    for x, y in route_loc[:-1]:
        send_POSITION(device, x, y)

    send_POSITION(device, route_loc[-1][0], route_loc[-1][1], last=True)

    if ANDROID_DEVICE == "BlueStack":
        sendevent(device, EV_SYN, SYN_MT_REPORT, 0)
    else:
        send_ABS_MT_TRACKING_ID(device, -1)
        send_BTN_TOUCH_UP(device)

    send_SYN_REPORT(device)


import subprocess
import time

class AdbEventController:
    def __init__(self, device: AdbDevice|None=None, dev: str=DEV):
        if device is None:
            self.device = get_adb_device()
        self.dev = dev
        self.adb_shell = subprocess.Popen(['adb', 'shell'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        self.time_between_events = 0.01
        self.time_between_moves = 0.05

        self.first_command = True
        self.long_command = ""

        print('AdbEventController initialized')


    def call(self, command):
        # print(f"called: {command}")
        # self.adb_shell.stdin.write(command + '\n')
        # self.adb_shell.stdin.write(command)
        # self.adb_shell.stdin.flush()

        os.system(f'"adb shell "{command}"')

    def add_command(self, command):
        # self.long_command += command + "\n"
        if self.first_command:
            self.long_command = command
            self.first_command = False
        else:
            self.long_command += " && " + command

    def send_long_command(self):
        self.call(self.long_command)
        self.long_command = ""
        self.first_command = True

    def sendevent(self, type: int, code: int, value: int):
        # self.call(f'sendevent {self.dev} {type} {code} {value}')
        self.add_command(f'sendevent {self.dev} {type} {code} {value}')

    def send_SYN_REPORT(self):
        self.sendevent(EV_SYN, SYN_REPORT, 0)

    def send_SYN_MT_REPORT(self):
        self.sendevent(EV_SYN, SYN_MT_REPORT, 0)

    def send_BTN_TOUCH_DOWN(self):
        self.sendevent(EV_KEY, BTN_TOUCH, 1)

    def send_BTN_TOUCH_UP(self):
        self.sendevent(EV_KEY, BTN_TOUCH, 0)

    def send_POSITION(self, x: int, y: int, last: bool=False):
        self.sendevent(EV_ABS, ABS_MT_POSITION_X, x)
        self.sendevent(EV_ABS, ABS_MT_POSITION_Y, y)
        if last and (ANDROID_DEVICE == "BlueStack" or ANDROID_DEVICE == "Nox"):
            self.send_SYN_MT_REPORT()
        self.send_SYN_REPORT()

    def send_ABS_MT_TRACKING_ID(self, x: int):
        self.sendevent(EV_ABS, ABS_MT_TRACKING_ID, x)

    def rand_loc(self):
        return random.randint(-RUNE_SIZE // 5, RUNE_SIZE // 5)
    
    def get_shell_response(self):
        output = []
        while True:
            line = self.adb_shell.stdout.readline()
            print(f"{line=}")
            if not line:
                break
            output.append(line)
            if line.strip() == '#':  # assuming shell prompt is '#'
                break

        return ''.join(output)

    def route_move(self, route):
        route_loc = [get_grid_loc(x, y) for x, y in route]
        route_loc = [(x + RUNE_SIZE // 2 + self.rand_loc(), y + RUNE_SIZE // 2 + self.rand_loc()) for x, y in route_loc]

        # weird coordinate system of emulators
        if ANDROID_DEVICE == "LdPlayer":
            route_loc = [(y, SCREEN_WIDTH - x) for x, y in route_loc]
        elif ANDROID_DEVICE == "BlueStack":
            route_loc = [(SCREEN_HEIGHT - y, x) for x, y in route_loc]
            route_loc = [(int(float(x) / SCREEN_HEIGHT * 32768), int(float(y) / SCREEN_WIDTH * 32768)) for x, y in route_loc]

        self.send_ABS_MT_TRACKING_ID(1)
        self.send_BTN_TOUCH_DOWN()

        for x, y in route_loc[:-1]:
            self.send_POSITION(x, y)
            # time.sleep(self.time_between_moves)

        self.send_POSITION(route_loc[-1][0], route_loc[-1][1], last=True)

        if ANDROID_DEVICE == "BlueStack":
            self.send_SYN_MT_REPORT()
        else:
            self.send_ABS_MT_TRACKING_ID(-1)
            self.send_BTN_TOUCH_UP()

        self.send_SYN_REPORT()
        self.add_command("echo 'end of route_move'")

        # print(f"{self.long_command=}")
        self.send_long_command()

        # wait for the shell to finish
        self.adb_shell.stdout.readline()


    def route_move_no_root(self, route):
        route_loc = [get_grid_loc(x, y) for x, y in route]
        route_loc = [(x + RUNE_SIZE // 2 + self.rand_loc(), y + RUNE_SIZE // 2 + self.rand_loc()) for x, y in route_loc]

        self.add_command(f"input motionevent DOWN {route_loc[0][0]} {route_loc[0][1]}")
        for x, y in route_loc[1:]:
            self.add_command(f"input motionevent MOVE {x} {y}")
            self.add_command(f"sleep {self.time_between_moves}")
            # time.sleep(self.time_between_events)
        self.add_command(f"input motionevent UP {route_loc[-1][0]} {route_loc[-1][1]}")
        # print(f"{self.long_command=}")
        self.send_long_command()


    def close(self):
        if self.adb_shell:
            self.adb_shell.stdin.close()
            self.adb_shell.stdout.close()
            self.adb_shell.stderr.close()
            self.adb_shell.kill()
            self.adb_shell.wait()
            self.adb_shell = None

    def __del__(self):
        self.close()
        print('AdbEventController deleted')
        