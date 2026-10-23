# KDE-Window-Tracker v1.1

CLI tool to log active window changes for productivity tracking similar to [ProcrastiTracker](https://strlen.com/procrastitracker/) and [ActivityWatch](https://activitywatch.net/). Works on KDE Plasma Wayland.

Tested on Arch2026.07.01, Debian 13, Fedora 44 with 

KDE Plasma 6.3.6 - 6.8.1

<img src="images/screen1.png" width="800">

## Requirements

KDE Plasma 6+

systemd

Python 3.14+

qdbus (qdbus6)

Depending on distribution

python3-dbus

python3-gi

## Install
```bash
git clone https://github.com/Divinux/KDE-Window-Tracker.git
cd KDE-Window-Tracker
chmod +x installer.sh
./installer.sh
```

## Uninstall
```bash
cd KDE-Window-Tracker
chmod +x uninstaller.sh
./uninstaller.sh
```

## Usage
To display stats
```bash
windowtracker
```

To display condensed stats
```bash
windowtracker -c
```

## Addons
The addons directory contains an optional script "trackercheck" which checks that:

1. The kwin script is installed and enabled,

2. The logger script is responsive

3. The systemd service is present and running

It can be sourced in for example .bashrc to alert in case anything breaks as such:

```bash
if [ -f ~/KDE-Window-Tracker/addons/trackercheck ]; then
    . ~/KDE-Window-Tracker/addons/trackercheck
fi
```

Further, "convertTimestamps.py" is needed to convert from v1.0 to the more condensed v1.1 log file format. If v1.0 was installed prior to installing v1.1:

```bash
cd KDE-Window-Tracker
uninstaller.sh
git pull
python addons/convertTimestamps.py
installer.sh
```


