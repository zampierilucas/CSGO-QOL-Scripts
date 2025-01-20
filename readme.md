# QOL-Scripts

## Overview
This script offers:
- Automatic match acceptance (League of Legends and, Counter-Strike).
- Automatic monitor brightness adjustments when playing certain games.

## Features
- Automatically detects the foreground application to dim or brighten secondary monitors.
- Accepts matches via image recognition or through game-specific APIs when possible.
- Configurable via a system tray icon, with toggles for auto accept and dimming.
- Simple, theme-aware GUI for selecting specific monitors to adjust.

## Installation
1. Install Python 3.x.
2. From the project root, install dependencies:
   ```bash
   pip install .
   ```
3. Run main.py with:
   ```bash
   python main.py
   ```

## Usage
1. The script runs in the system tray.
2. Right-click the tray icon to:
   - Configure settings (dimming and auto-accept).
   - Toggle features on or off.
   - Access “About” to view the repository link.
3. Edit settings.json or use the GUI to specify dimmable monitors and apps to dim.

## Contributing
Feel free to submit issues or pull requests on GitHub.

## License
This project is MIT-Licensed. See the LICENSE file for details.
