#!/usr/bin/env bash
# Fix permissions so the current user can read JX-11 input devices and write to uinput.
set -e

USER_NAME="${SUDO_USER:-$USER}"

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run with sudo. Try:"
    echo "  sudo ./setup-permissions.sh"
    exit 1
fi

echo "Setting up permissions for user: $USER_NAME"

# 1. Add user to input group
if ! id -nG "$USER_NAME" | grep -qw input; then
    usermod -aG input "$USER_NAME"
    echo "Added $USER_NAME to 'input' group."
else
    echo "$USER_NAME is already in 'input' group."
fi

# 2. udev rule for uinput (virtual keyboard output)
if [ ! -f /etc/udev/rules.d/99-uinput.rules ]; then
    echo 'KERNEL=="uinput", MODE="0660", GROUP="input"' > /etc/udev/rules.d/99-uinput.rules
    echo "Created udev rule for /dev/uinput."
fi

# 3. udev rule for JX-11 Bluetooth devices specifically
# This ensures the input group can read them even before log out/in
if [ ! -f /etc/udev/rules.d/99-jx11-input.rules ]; then
    cat > /etc/udev/rules.d/99-jx11-input.rules <<'EOF'
# JX-11 Bluetooth ring — grant input group access
SUBSYSTEM=="input", ATTRS{name}=="JX-11*", MODE="0660", GROUP="input"
SUBSYSTEM=="input", ATTRS{uniq}=="52:f8:0e:22:06:f2", MODE="0660", GROUP="input"
EOF
    echo "Created udev rule for JX-11 devices."
fi

# 4. Reload udev rules
udevadm control --reload-rules
udevadm trigger --subsystem-match=input

echo ""
echo "Done. You MUST log out and log back in for the group change to take effect."
echo "After re-logging, run:  ~/.local/bin/jx11-remapper"
echo ""
echo "To test without re-logging (temporary):"
echo "  sudo setfacl -m u:\$USER:rw /dev/input/event* /dev/uinput"
