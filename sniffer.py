#!/usr/bin/env python3
"""Pure-Python JX-11 event sniffer — no external dependencies."""
import os
import select
import struct
import sys

EVENT_FORMAT = "llHHi"  # 64-bit timeval + type + code + value
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03
EV_MSC = 0x04

TYPE_NAMES = {EV_SYN: "SYN", EV_KEY: "KEY", EV_REL: "REL", EV_ABS: "ABS", EV_MSC: "MSC"}

# A few common key names for quick reference
KEY_NAMES = {
    113: "MUTE", 114: "VOLUMEDOWN", 115: "VOLUMEUP", 116: "POWER",
    128: "STOP", 139: "MENU", 150: "WWW", 158: "BACK", 159: "FORWARD",
    163: "NEXTSONG", 164: "PLAYPAUSE", 165: "PREVIOUSSONG",
    172: "HOMEPAGE", 176: "EDIT", 177: "SCROLLUP", 178: "SCROLLDOWN",
    217: "PLAY", 223: "CANCEL", 256: "BTN_0", 353: "SELECT",
    362: "CHANNELUP", 370: "ZOOMIN", 380: "NEWS", 384: "DISPLAYTOGGLE",
    396: "MEDIA", 400: "PICKUP_PHONE", 401: "HANGUP_PHONE",
    403: "APPSELECT", 416: "MICMUTE", 418: "DASHBOARD", 419: "CONTACTS",
}

REL_NAMES = {6: "HWHEEL", 8: "WHEEL", 11: "WHEEL_HI_RES", 12: "HWHEEL_HI_RES"}
ABS_NAMES = {0: "X", 1: "Y", 47: "MT_TOUCH_MAJOR", 53: "MT_POSITION_X",
             54: "MT_POSITION_Y", 57: "MT_TRACKING_ID"}


def find_devices():
    devs = []
    for f in os.listdir("/sys/class/input/"):
        if not f.startswith("event"):
            continue
        uevent = f"/sys/class/input/{f}/device/uevent"
        try:
            with open(uevent) as fp:
                if "JX-11" in fp.read():
                    devs.append(f"/dev/input/{f}")
        except FileNotFoundError:
            pass
    return devs


def name(code, table):
    return table.get(code, str(code))


def main():
    devices = find_devices()
    if not devices:
        print("No JX-11 devices found in /sys/class/input")
        sys.exit(1)

    print(f"Found: {devices}")
    print("Press buttons / scroll on the ring. Ctrl-C to stop.\n")

    fds = {}
    for path in devices:
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
            fds[fd] = path
        except PermissionError:
            print(f"Permission denied: {path} (try running as root or adding user to 'input' group)")

    if not fds:
        sys.exit(1)

    try:
        while True:
            readable, _, _ = select.select(fds.keys(), [], [], 1.0)
            for fd in readable:
                path = fds[fd]
                data = os.read(fd, EVENT_SIZE)
                if len(data) != EVENT_SIZE:
                    continue
                _, _, typ, code, value = struct.unpack(EVENT_FORMAT, data)
                if typ == EV_SYN:
                    continue
                tname = TYPE_NAMES.get(typ, f"EV_{typ}")
                if typ == EV_KEY:
                    cname = name(code, KEY_NAMES)
                    action = "press" if value == 1 else "release" if value == 0 else "repeat"
                    print(f"{path}: {tname}.{cname} {action}")
                elif typ == EV_REL:
                    cname = name(code, REL_NAMES)
                    print(f"{path}: {tname}.{cname} delta={value}")
                elif typ == EV_ABS:
                    cname = name(code, ABS_NAMES)
                    print(f"{path}: {tname}.{cname} value={value}")
                else:
                    print(f"{path}: {tname}.{code} value={value}")
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        for fd in fds:
            os.close(fd)


if __name__ == "__main__":
    main()
