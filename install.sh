#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p ~/.config/jx11-remapper
mkdir -p ~/.local/bin
mkdir -p ~/.config/systemd/user

cp "$SCRIPT_DIR/jx11-remapper" ~/.local/bin/
chmod +x ~/.local/bin/jx11-remapper
cp "$SCRIPT_DIR/jx11-remapper-gui" ~/.local/bin/
chmod +x ~/.local/bin/jx11-remapper-gui

if [ ! -f ~/.config/jx11-remapper/config.toml ]; then
    cp "$SCRIPT_DIR/config.default.toml" ~/.config/jx11-remapper/config.toml
    echo "Created default config at ~/.config/jx11-remapper/config.toml"
else
    echo "Config already exists at ~/.config/jx11-remapper/config.toml (not overwritten)"
fi

cp "$SCRIPT_DIR/jx11-remapper.service" ~/.config/systemd/user/

systemctl --user daemon-reload
systemctl --user enable jx11-remapper.service

echo ""
echo "Install complete."
echo ""
echo "  IMPORTANT: Run this first:"
echo "    sudo $SCRIPT_DIR/setup-permissions.sh"
echo "    # Then log out and log back in"
echo ""
echo "  (setup-permissions.sh is at: $SCRIPT_DIR/setup-permissions.sh)"
echo ""
echo "  Check ready:   ~/.local/bin/jx11-remapper --check"
echo "  Open GUI:      ~/.local/bin/jx11-remapper-gui"
echo "  Start daemon:  systemctl --user start jx11-remapper"
echo "  View logs:     journalctl --user -u jx11-remapper -f"
echo ""
echo "Make sure python-evdev is installed:"
echo "  sudo pacman -S python-evdev   # CachyOS / Arch"
