#!/usr/bin/env bash

# 1. Find the absolute directory of the executing script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
KWIN_SCRIPT_PATH="$SCRIPT_DIR/kwin.windowtracker"

echo "Installing KWin script from: $KWIN_SCRIPT_PATH"

# Install the KWin script and enable it
kpackagetool6 -t KWin/Script -i "$KWIN_SCRIPT_PATH"
kwriteconfig6 --file kwinrc --group Plugins --key kwin.windowtrackerEnabled true
qdbus6 org.kde.KWin /KWin org.kde.KWin.reconfigure

# 2. Define the target installation directory for the Python scripts
INSTALL_DIR="$HOME/.local/share/kwin.windowtracker"

echo "Installing Python scripts to: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy the scripts folder over
cp -r "$SCRIPT_DIR/scripts" "$INSTALL_DIR/"

# Make the Python scripts executable
chmod +x "$INSTALL_DIR/scripts/"*.py

# 3. Setup the systemd service
SYSTEMD_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SYSTEMD_DIR/windowtracker.service"

echo "Creating systemd service at: $SERVICE_FILE"
mkdir -p "$SYSTEMD_DIR"

# Use a "Here-Doc" to write the file.
# Variables like $INSTALL_DIR will automatically be expanded.
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=KWin Active Window D-Bus Logger Daemon
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/env python3 "$INSTALL_DIR/scripts/logger.py"
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical-session.target
EOF

# 4. Enable and start the systemd service
echo "Reloading systemd and enabling the service..."
systemctl --user daemon-reload
systemctl --user enable --now windowtracker.service

echo "Installation complete! The tracker should now be running."
systemctl --user status windowtracker.service

# 5. Add a helper script to enable running window-analyzer
# Create the bin directory if it doesn't exist
mkdir -p "$HOME/.local/bin"

# 2. Write the wrapper script
cat <<EOF > "$HOME/.local/bin/windowtracker"
#!/usr/bin/env bash
exec /usr/bin/env python3 "$INSTALL_DIR/scripts/analyzer.py" "\$@"
EOF

# 3. Make it executable
chmod +x "$HOME/.local/bin/windowtracker"

# 4. Inform the user
echo "Helper script installed to ~/.local/bin/windowtracker"
echo "Note: Ensure '~/.local/bin' is in your \$PATH."
