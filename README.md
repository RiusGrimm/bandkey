# Bandkey — JX-11 Bluetooth Ring Key Remapper

**Codename:** Bandkey  
**Repository:** https://github.com/RiusGrimm/bandkey  
**What it does:** Turns a JX-11 Bluetooth smart ring into a fully customisable human-interface device for Linux. The daemon grabs the ring's raw input, intercepts its media-key events, and remaps them to arbitrary keyboard keys via a virtual `uinput` keyboard. This works on Wayland, X11, and the Linux console.

## Key behaviour — Toggle, not tap

By default, **all physical buttons on the ring act as toggles**:

| Physical control | What happens |
|---|---|
| **Side buttons** (centre/select) | Press once → virtual key is **held down**. Press the same button again → virtual key **released**. |
| **Wheel centre tap** | Tap once → virtual key is **held down**. Tap the centre again → virtual key **released**. |
| **Wheel swipe** (left/right/up/down) | Swipe in a direction → virtual key is **tapped once** (discrete press + release). |

This toggle model is ideal for **push-to-talk** (PTT), **push-to-mute**, or any situation where you want a key to stay pressed without holding your finger on a tiny ring surface.

## Pre-built profiles

| Profile | wheel/swipe | centre tap | side buttons |
|---|---|---|---|
| **Media Controls** | volume up / down, prev / next track | play/pause | mute |
| **Keyboard Backtick (`)** | no-op | `` ` `` (Grave) | `` ` `` (Grave) |
| **Voice AI (Riff)** | volume up / down | backspace / enter | Esc |
| **Custom** | whatever you set via the GUI | whatever you set via the GUI | whatever you set via the GUI |

## Quick start

### 1. Fix permissions (one-time)

The daemon needs to read raw input devices and create a virtual keyboard.

```bash
sudo ./setup-permissions.sh
```

**Then log out and log back in.** Group changes only take effect on a fresh login session.

### 2. Install the dependency

```bash
sudo pacman -S python-evdev      # CachyOS / Arch
# or
sudo apt install python3-evdev   # Debian / Ubuntu
```

### 3. Install Bandkey

```bash
./install.sh
```

This copies the daemon, the GUI, and the systemd service file to their correct homes under `~/.local/`.

### 4. Check readiness

```bash
~/.local/bin/jx11-remapper --check
```

Everything should show a green ✓. If not, re-run `setup-permissions.sh` and log out/in again.

### 5. Configure

Open the desktop GUI:

```bash
~/.local/bin/jx11-remapper-gui
```

Pick a profile, change any mapping, hit **Test** to try a key, then **Save & Restart Daemon**.

Or edit the TOML directly:

```bash
nano ~/.config/jx11-remapper/config.toml
```

### 6. Run the daemon

```bash
systemctl --user start jx11-remapper
systemctl --user enable jx11-remapper    # auto-start on login
journalctl --user -u jx11-remapper -f    # watch logs
```

## Config reference

```toml
[device]
name = "JX-11"
mac  = "52:f8:0e:22:06:f2"

[gestures]
scroll_up     = "XF86AudioRaiseVolume"
scroll_down   = "XF86AudioLowerVolume"
button_left   = "XF86AudioPrev"
button_right  = "XF86AudioNext"
button_center = "XF86AudioPlay"
center_button = "XF86AudioMute"
select_button = ""
```

Key names are Linux evdev constants without the `KEY_` prefix. Chords use `+`:

```toml
button_center = "LeftCtrl+LeftShift+Enter"
```

## Files

| File | Purpose |
|---|---|
| `jx11-remapper` | Single-file Python daemon (~600 lines). Handles device discovery, exclusive grab, event translation, and virtual-keyboard emission. |
| `jx11-remapper-gui` | Tkinter desktop GUI for picking profiles and editing key mappings. |
| `sniffer.py` | Standalone evdev sniffer for debugging your ring's raw events. |
| `setup-permissions.sh` | Adds your user to the `input` group and creates udev rules. |
| `install.sh` | Copies binaries, config template, and systemd service into place. |
| `jx11-remapper.service` | systemd user unit for auto-start. |
| `config.default.toml` | Default configuration template. |

## How it works

1. **Discovery** — Scans `/sys/class/input` for nodes matching the configured ring `name` or Bluetooth `mac`.
2. **Exclusive grab** — Opens every matching device with `EVIOCGRAB` so the desktop never sees the original media-key events.
3. **Translation** — Creates a virtual keyboard via `uinput` and maps ring gestures to keyboard keys.
4. **Auto-reconnect** — If the ring disconnects (Bluetooth timeout, out of range, powered off) the daemon notices within a couple of seconds and polls until it re-appears.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Permission denied` on `/dev/input/*` | Run `setup-permissions.sh`, then **log out and back in**. |
| Ring still changes system volume | The daemon failed to grab the device. Check `journalctl --user -u jx11-remapper`. |
| `python-evdev not installed` | Install `python-evdev` (see Quick Start step 1). |
| Wrong button mapping | Run `python3 sniffer.py`, press each control, note the codes, and edit `config.toml`. |
| Daemon won't start after edits | `python3 -m py_compile jx11-remapper` will catch any syntax errors before you push. |

## License

MIT — hack it freely.
