#!/usr/bin/env bash

# 1. Define paths (must match the installer paths)
INSTALL_DIR="$HOME/.local/share/kwin.windowtracker"
SYSTEMD_SERVICE="$HOME/.config/systemd/user/windowtracker.service"

echo "Starting uninstallation..."

# 2. Stop and Disable the systemd service
if [ -f "$SYSTEMD_SERVICE" ]; then
    echo "Stopping and disabling systemd service..."
    systemctl --user stop windowtracker.service
    systemctl --user disable windowtracker.service
    rm "$SYSTEMD_SERVICE"
    systemctl --user daemon-reload
    systemctl --user reset-failed
fi

# 3. Remove the KWin script
# We use the plugin name to tell kpackagetool6 to remove it
echo "Removing KWin script..."
kpackagetool6 -t KWin/Script -r kwin.windowtracker 2>/dev/null

# Disable the config key in kwinrc
kwriteconfig6 --file kwinrc --group Plugins --key kwin.windowtrackerEnabled --delete

# Trigger KWin to reconfigure
qdbus6 org.kde.KWin /KWin org.kde.KWin.reconfigure

# 4. Remove the installation directory
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing installation files from $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
fi

# 5. Remove the helper script
if [ -f "$HOME/.local/bin/window-analyzer" ]; then
    echo "Removing helper script..."
    rm "$HOME/.local/bin/window-analyzer"
fi

echo "Uninstallation complete. Your system has been cleaned up."
