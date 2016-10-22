# !/usr/bin/python

import signal
import sys
import asyncio
import evdev
from time import localtime, strftime
import os

keyboard_handler = evdev.InputDevice('/dev/input/event0')
mouse_handler = keyboard_handler
keyboard_log_dir = "keyboard_log_dir/"
glidePoint_log_dir = "glidePoint_log_dir/"


# mouse event handler may vary
def initialize_mouse_event():
    global mouse_handler
    events = open("/proc/bus/input/devices")
    file = events.read()
    device_info = file.split("\n\n")
    device_list = list()
    for device in device_info:
        # list of device info
        # each element is list of info strings
        device_list.append(device.split("\n"))
    device_list = device_list[:-1]
    for device in device_list:
        if str(device[5]).find("mouse") > -1:
            mouse_handler = evdev.InputDevice("/dev/input/" + str(device[5]).split()[1][9:])
            break


def create_dirs():
    if os.chdir(keyboard_log_dir):
        os.chdir("..")
    else:
        os.mkdir(keyboard_log_dir)
    if os.chdir(glidePoint_log_dir):
        os.chdir("..")
    else:
        os.mkdir(glidePoint_log_dir)


async def print_events(device, keyboard_log_file, mouse_log_file):
    async for event in device.async_read_loop():
        categorized = evdev.categorize(event)

        if str(categorized)[-4:] == "down":
            if device.fn == keyboard_handler.fn:
                keyboard_log_file.write(str(categorized) + "\n")
            else:
                mouse_log_file.write(str(categorized) + "\n")
            print(categorized)


if __name__ == '__main__':
    # create_dirs()
    keyboard_log_file = open(keyboard_log_dir + "keyboard_log_" + strftime("%Y-%m-%d_%H:%M:%S", localtime()), "w")
    mouse_log_file = open(glidePoint_log_dir + "glidePoint_log_" + strftime("%Y-%m-%d_%H:%M:%S", localtime()), "w")

    def signal_handler(signal, frame):
        keyboard_log_file.close()
        mouse_log_file.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    initialize_mouse_event()

    for device in mouse_handler, keyboard_handler:
        asyncio.ensure_future(print_events(device, keyboard_log_file, mouse_log_file))

    loop = asyncio.get_event_loop()
    loop.run_forever()
