# KDE-Window-Tracker

CLI tool to log active window changes for productivity tracking similar to [ProcrastiTracker](https://strlen.com/procrastitracker/) and [ActivityWatch](https://activitywatch.net/). Works on KDE Plasma Wayland.

Tested on Arch2026.07.01, Debian 13, Fedora 44

<img src="images/screen1.png" width="800">

# Requirements

KDE Plasma 6+

systemd

qdbus (qdbus6)

Depending on distribution

python3-dbus

python3-gi

# Install
```bash
git clone https://github.com/Divinux/KDE-Window-Tracker.git
cd KDE-Window-Tracker
chmod +x installer.sh
./installer.sh
```

# Uninstall
```bash
cd KDE-Window-Tracker
chmod +x uninstaller.sh
./uninstaller.sh
```

# Usage
To display stats
```bash
windowtracker
```

To display condensed stats
```bash
windowtracker -c
```





