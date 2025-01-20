import pyautogui
import time
import screen_brightness_control as sbc
from win32gui import GetWindowText, GetForegroundWindow
from win32con import WM_INPUTLANGCHANGEREQUEST
import os
import logging
import requests
from requests.auth import HTTPBasicAuth
import base64
import pystray
from PIL import Image
import json
from threading import Thread
import tkinter as tk
from tkinter import ttk
import appdirs
import pathlib
import signal
import win32gui
import tempfile
import argparse
import sv_ttk
import darkdetect
import pywinstyles, sys
import webbrowser

PROGRAM_NAME = "QOL-Scripts"
CONFIG_DIR = pathlib.Path(appdirs.user_config_dir(PROGRAM_NAME))
CONFIG_FILE = CONFIG_DIR / "settings.json"

# Disable "unverified HTTPS request" warnings
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

# ----------------------------------
# 1) LOGGING SETUP
# ----------------------------------
def setup_logging(debug=False):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    # Suppress specific warning logs
    logging.getLogger("screen_brightness_control").setLevel(logging.ERROR)
    return logger

# ----------------------------------
# 3) CS ACCEPT-IMAGE / UTILS
encoded_accept_cs = "iVBORw0KGgoAAAANSUhEUgAAAOMAAABaCAYAAABKS+HxAAAKT2lDQ1BQaG90b3Nob3AgSUNDIHByb2ZpbGUAAHjanVNnVFPpFj333vRCS4iAlEtvUhUIIFJCi4AUkSYqIQkQSoghodkVUcERRUUEG8igiAOOjoCMFVEsDIoK2AfkIaKOg6OIisr74Xuja9a89+bN/rXXPues852zzwfACAyWSDNRNYAMqUIeEeCDx8TG4eQuQIEKJHAAEAizZCFz/SMBAPh+PDwrIsAHvgABeNMLCADATZvAMByH/w/qQplcAYCEAcB0kThLCIAUAEB6jkKmAEBGAYCdmCZTAKAEAGDLY2LjAFAtAGAnf+bTAICd+Jl7AQBblCEVAaCRACATZYhEAGg7AKzPVopFAFgwABRmS8Q5ANgtADBJV2ZIALC3AMDOEAuyAAgMADBRiIUpAAR7AGDIIyN4AISZABRG8lc88SuuEOcqAAB4mbI8uSQ5RYFbCC1xB1dXLh4ozkkXKxQ2YQJhmkAuwnmZGTKBNA/g88wAAKCRFRHgg/P9eM4Ors7ONo62Dl8t6r8G/yJiYuP+5c+rcEAAAOF0ftH+LC+zGoA7BoBt/qIl7gRoXgugdfeLZrIPQLUAoOnaV/Nw+H48PEWhkLnZ2eXk5NhKxEJbYcpXff5nwl/AV/1s+X48/Pf14L7iJIEyXYFHBPjgwsz0TKUcz5IJhGLc5o9H/LcL//wd0yLESWK5WCoU41EScY5EmozzMqUiiUKSKcUl0v9k4t8s+wM+3zUAsGo+AXuRLahdYwP2SycQWHTA4vcAAPK7b8HUKAgDgGiD4c93/+8//UegJQCAZkmScQAAXkQkLlTKsz/HCAAARKCBKrBBG/TBGCzABhzBBdzBC/xgNoRCJMTCQhBCCmSAHHJgKayCQiiGzbAdKmAv1EAdNMBRaIaTcA4uwlW4Dj1wD/phCJ7BKLyBCQRByAgTYSHaiAFiilgjjggXmYX4IcFIBBKLJCDJiBRRIkuRNUgxUopUIFVIHfI9cgI5h1xGupE7yAAygvyGvEcxlIGyUT3UDLVDuag3GoRGogvQZHQxmo8WoJvQcrQaPYw2oefQq2gP2o8+Q8cwwOgYBzPEbDAuxsNCsTgsCZNjy7EirAyrxhqwVqwDu4n1Y8+xdwQSgUXACTYEd0IgYR5BSFhMWE7YSKggHCQ0EdoJNwkDhFHCJyKTqEu0JroR+cQYYjIxh1hILCPWEo8TLxB7iEPENyQSiUMyJ7mQAkmxpFTSEtJG0m5SI+ksqZs0SBojk8naZGuyBzmULCAryIXkneTD5DPkG+Qh8lsKnWJAcaT4U+IoUspqShnlEOU05QZlmDJBVaOaUt2ooVQRNY9aQq2htlKvUYeoEzR1mjnNgxZJS6WtopXTGmgXaPdpr+h0uhHdlR5Ol9BX0svpR+iX6AP0dwwNhhWDx4hnKBmbGAcYZxl3GK+YTKYZ04sZx1QwNzHrmOeZD5lvVVgqtip8FZHKCpVKlSaVGyovVKmqpqreqgtV81XLVI+pXlN9rkZVM1PjqQnUlqtVqp1Q61MbU2epO6iHqmeob1Q/pH5Z/YkGWcNMw09DpFGgsV/jvMYgC2MZs3gsIWsNq4Z1gTXEJrHN2Xx2KruY/R27iz2qqaE5QzNKM1ezUvOUZj8H45hx+Jx0TgnnKKeX836K3hTvKeIpG6Y0TLkxZVxrqpaXllirSKtRq0frvTau7aedpr1Fu1n7gQ5Bx0onXCdHZ4/OBZ3nU9lT3acKpxZNPTr1ri6qa6UbobtEd79up+6Ynr5egJ5Mb6feeb3n+hx9L/1U/W36p/VHDFgGswwkBtsMzhg8xTVxbzwdL8fb8VFDXcNAQ6VhlWGX4YSRudE8o9VGjUYPjGnGXOMk423GbcajJgYmISZLTepN7ppSTbmmKaY7TDtMx83MzaLN1pk1mz0x1zLnm+eb15vft2BaeFostqi2uGVJsuRaplnutrxuhVo5WaVYVVpds0atna0l1rutu6cRp7lOk06rntZnw7Dxtsm2qbcZsOXYBtuutm22fWFnYhdnt8Wuw+6TvZN9un2N/T0HDYfZDqsdWh1+c7RyFDpWOt6azpzuP33F9JbpL2dYzxDP2DPjthPLKcRpnVOb00dnF2e5c4PziIuJS4LLLpc+Lpsbxt3IveRKdPVxXeF60vWdm7Obwu2o26/uNu5p7ofcn8w0nymeWTNz0MPIQ+BR5dE/C5+VMGvfrH5PQ0+BZ7XnIy9jL5FXrdewt6V3qvdh7xc+9j5yn+M+4zw33jLeWV/MN8C3yLfLT8Nvnl+F30N/I/9k/3r/0QCngCUBZwOJgUGBWwL7+Hp8Ib+OPzrbZfay2e1BjKC5QRVBj4KtguXBrSFoyOyQrSH355jOkc5pDoVQfujW0Adh5mGLw34MJ4WHhVeGP45wiFga0TGXNXfR3ENz30T6RJZE3ptnMU85ry1KNSo+qi5qPNo3ujS6P8YuZlnM1VidWElsSxw5LiquNm5svt/87fOH4p3iC+N7F5gvyF1weaHOwvSFpxapLhIsOpZATIhOOJTwQRAqqBaMJfITdyWOCnnCHcJnIi/RNtGI2ENcKh5O8kgqTXqS7JG8NXkkxTOlLOW5hCepkLxMDUzdmzqeFpp2IG0yPTq9MYOSkZBxQqohTZO2Z+pn5mZ2y6xlhbL+xW6Lty8elQfJa7OQrAVZLQq2QqboVFoo1yoHsmdlV2a/zYnKOZarnivN7cyzytuQN5zvn//tEsIS4ZK2pYZLVy0dWOa9rGo5sjxxedsK4xUFK4ZWBqw8uIq2Km3VT6vtV5eufr0mek1rgV7ByoLBtQFr6wtVCuWFfevc1+1dT1gvWd+1YfqGnRs+FYmKrhTbF5cVf9go3HjlG4dvyr+Z3JS0qavEuWTPZtJm6ebeLZ5bDpaql+aXDm4N2dq0Dd9WtO319kXbL5fNKNu7g7ZDuaO/PLi8ZafJzs07P1SkVPRU+lQ27tLdtWHX+G7R7ht7vPY07NXbW7z3/T7JvttVAVVN1WbVZftJ+7P3P66Jqun4lvttXa1ObXHtxwPSA/0HIw6217nU1R3SPVRSj9Yr60cOxx++/p3vdy0NNg1VjZzG4iNwRHnk6fcJ3/ceDTradox7rOEH0x92HWcdL2pCmvKaRptTmvtbYlu6T8w+0dbq3nr8R9sfD5w0PFl5SvNUyWna6YLTk2fyz4ydlZ19fi753GDborZ752PO32oPb++6EHTh0kX/i+c7vDvOXPK4dPKy2+UTV7hXmq86X23qdOo8/pPTT8e7nLuarrlca7nuer21e2b36RueN87d9L158Rb/1tWeOT3dvfN6b/fF9/XfFt1+cif9zsu72Xcn7q28T7xf9EDtQdlD3YfVP1v+3Njv3H9qwHeg89HcR/cGhYPP/pH1jw9DBY+Zj8uGDYbrnjg+OTniP3L96fynQ89kzyaeF/6i/suuFxYvfvjV69fO0ZjRoZfyl5O/bXyl/erA6xmv28bCxh6+yXgzMV70VvvtwXfcdx3vo98PT+R8IH8o/2j5sfVT0Kf7kxmTk/8EA5jz/GMzLdsAAAAgY0hSTQAAeiUAAICDAAD5/wAAgOkAAHUwAADqYAAAOpgAABdvkl/FRgAADJpJREFUeNrsnWtsHNUVx//nzuyu7fixduzYTmI7zhMnJCEJoWlCE1JIIRISH6BVVbWo7yL6oQX1Q+mHVqgtaqt+QCqiD6mpVIgQVFRtoaKB8EogvAmJHSfOy7Exfifr13r92Lm3H/bhXe/M2muvd+/G5yetvDsz9557z8zxuefMvTNUebNXKaUAhfBHgJQCiAAFKIT3QUFGfiP0O7orhkg1kSPV9AMQqppAEDG/BQgEAiimonAdMlKfSqyIQDCIYJCI1mMQorUThb4RASGp0cIgiq+QpvZM/Q4VhCCbA6PttOnjVFFQjF6UQkiP0c5QqN00pZc4PYZ1HjlFUk3X4xShegEJCakiZVTcMfHNDp+jmE4Q4tscqVeG2yCVimmPCvczpGNBAiYRBAEuYcAgghACRvi8iEhfw39B03U9XbmpoGIvS8dzMnV0uA9KxVyzU+efiKL6pUhjp2tvmqzY8xfbqch1HrmIVPhCkOGPBQkLCiYpQCnC+q9tQXGdF8IUYBhm4VGWRKBtCL3PnYeEgqCwIXrXlLEhMkwGIUOgYLUX5V9eh2DQggAUiuu8rBmGyRIFdSWYlBICitgjMkwWEaaAZVkQyjHcZRgmU0hLQSjFxsgw2UYpBRGXK2cYJkvWSBCSh6kMk3UIBMGjVIbJPoIEhGQ9MEz2PaMQnE1lGB6mMgwTb4ycwGGY7KMA8NQbhtEASyk2RobRwhgti42RYfTwjBJi7os5GYZJF0HFnpFh9PCMUkFEnw3BMEzWUFDxj3ZhGCZ75sjGyDAaEPuANoZhsoggNkaG0cQYeQYOw+hhjDxMZRgepjIMw8bIMPpBEGyMDKOFMXICh2E0GaYCEGyNDKOHZzRzcdWGv8ePSf+EQ6cIJfXeBZM92uvHaN8oAr4AgoFJKAm48k24izwoWLYEBeUFMDyGVrKUpRDwBebVFvcSN8x8c171C4NguA0YbhPClZobGO0fTb8BCEJ+Wb42UaMpctAYX3/glaT77zh0J/JK06fkieFxdJzoQPOfGmd1fNXty7Fydw0qNlXA8JhZl+XvHcEbD746Lx1sf2Qnlt+yIm31u5e7Ubu/HlU7quCtL0167KR/Eq997+W0X0eelR4c+MNBfTyjyLFVG8MdQzMe09/ch5V7aucvTAFXXmtF0xOnUirW/Wonul/tBADseuxWlDeU6yVLAyY6J3DxcAsuHm6Bq9KFXT/dg5JVXixWCAThEmZONbr7ZPeMx7Q8f3becoJjQZz4zVspG8d0CiuXaCVLRyZ7JnH8oTfw2bsdizhoBITLyKEUjgJaDjXPeFigNQB/j3/OYqwJC2//8hiuvd8/r+ZW7q9G3gwxSSZl6c7J336IaxeuLVrPaJqUO55xoNVnu736wAp0vfJZ3Lbe0z2oP7B6TnLOHG7EcLPzcNgsN7H+vgYUlOeDDIGJoXH0Nvai62h8G1YfWKOVLDtW3FUzu/iq2DPv+ieGx9H3dm/S4z98/F0ceOIgKCZ8IgEUb/EmiSknELhkn+BJVq6wqlAnxwjTzKGbG10fdiZsq71nFaq2VycY45knT8/JGPvP9qP9P1cc9+/61R6Ub6pI2F6ztw7Wd7ejr6kXzc82YfSCH2Xrl2ojy+lC3faDHQt2vmzr/wkw0jWCpqdOof+dPttYcvDKILwxGXEz34W9j97mKGfMF8DRbx+x3ZesnHaekXIkgSODEpeeuZCwvWpblWPgP/TpEIprilOS88Hv3nHc98W/fAkFFQWO+w2Pgaod1ajaUY0x3xjIIG1k6URhdSFueWgX/tf4X8iRxLe9XDt/Nc4YFwsiV54n7nOIJUrqS+Ep9qBka+LJ6znZlbIMa8Cy91K/3pPUOKaTV5qnjSwtLzyXgS0PbLPdN9I5vBjzNxBS5sZ7qDpOfJqwbcmGwmgsU28TM7X87SxUCi+Ddcrmld1SjvKNFWntTyZl6coSh+zvSPfIYszgQEzmgDEGA0F8+mJbwvY1B9dNXcTry+yTPpd9sxOigCv/vGy7a81da9PboUzK0vn6cwiRzDwTixEhVVD7Rl5tsU/7xyYtCiqWQBQmJqM63/9sVjJGrzpPt/KuKU1rfzIpS2f8ffa3n1IZol9PmFYOeMa21684JgJiafjGJpz5Y/w0stZ/XMIN922E4U4+h3PMN+a4b65pfR1kJWPo9ACan2ma8biilcWo+UJtWmXLoETjXz+xzwPUeRenMer+stTxoXH0HkucdbPhmw0J25Y2VDgmS+xuEcTJGbQ3kKWfS3/8lklZM3H5uYszHlNzd11ajXF8aByNfz+FYL/9qKx0beniNEZD8wZePWs/R"

def accept_match(img_base64):
    """
    Accept a match by:
      1) Decoding base64-encoded image
      2) Locating the image on screen
      3) Clicking if found
    """
    try:
        img_data = base64.b64decode(img_base64 + "=" * (-len(img_base64) % 4))  # Fix padding
        # Use temp file for the image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(img_data)
            temp_file.flush()
            
            accept_btn = pyautogui.locateCenterOnScreen(
                temp_file.name,
                confidence=0.8
            )
            
            if accept_btn is not None:
                pyautogui.click(accept_btn)
                pyautogui.move(0, 300)
                logger.debug("Match accepted via image recognition (CS).")
            else:
                logger.debug("CS accept button not found on screen.")
            
            # Clean up temp file
            os.unlink(temp_file.name)
    except Exception as e:
        logger.error(f"Error in accept_match: {str(e)}")

def set_brigtness_side_monitors(brightness, monitor_ids):
    """
    Sets the brightness for any side monitors configured in settings
    """
    for monitor_id in monitor_ids:
        try:
            sbc.set_brightness(brightness, display=monitor_id)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Set brightness to {brightness} for monitor ID {monitor_id}")
        except Exception as e:
            logger.error(f"Failed to set brightness for monitor ID {monitor_id}: {e}")

# ----------------------------------
# 4) LCU (LEAGUE CLIENT) HELPER
# ----------------------------------
def league_client_is_open():
    """
    Returns True if the League lockfile exists, indicating the client is running.
    """
    lockfile_path = r"C:\Riot Games\League of Legends\lockfile"  # Adjust if needed
    return os.path.exists(lockfile_path)

def accept_lol_via_lcu():
    """
    Accept a League of Legends match via the local League Client API (LCU).
    This function:
      1) Reads the 'lockfile' to obtain port & credentials
      2) Sends a POST to /lol-matchmaking/v1/ready-check/accept
    """
    lockfile_path = r"C:\Riot Games\League of Legends\lockfile"  # adjust if needed

    # lockfile must exist if league_client_is_open() is True
    with open(lockfile_path, "r") as lf:
        content = lf.read().strip().split(':')

    if len(content) != 5:
        raise ValueError(f"Lockfile did not have the expected format. Got: {content}")

    process_name, pid, port, password, protocol = content
    url = f"{protocol}://127.0.0.1:{port}/lol-matchmaking/v1/ready-check/accept"
    auth = HTTPBasicAuth('riot', password)

    logger.debug("Attempting to accept LoL match via local client API...")
    response = requests.post(url, auth=auth, verify=False)

    if response.status_code in (200, 201, 204):
        logger.debug("LoL match accepted successfully (LCU).")
    else:
        logger.debug(
            f"LoL match accept call returned status {response.status_code}. "
            f"Response text: {response.text}"
        )

# ----------------------------------
# 5) MAIN LOOP
# ----------------------------------
class Settings:
    DEFAULT_SETTINGS = {
        "dimmable_monitors": [], 
        "monitor_brightness": {
            "high": 100,
            "low": 10
        },
        "games_to_dimm": [
            "League of Legends (TM) Client",
            "EscapeFromTarkov",
            "Counter-Strike 2",
            "Hell Let Loose"
        ],
        "dimming_enabled": True, 
        "auto_accept_enabled": True  
    }
    
    def __init__(self):
        # Create config directory if it doesn't exist
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.settings_file = CONFIG_FILE
        self.load_settings()

    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                self.data = json.load(f)
                # Migrate existing settings if dimming_enabled is missing
                if "dimming_enabled" not in self.data:
                    self.data["dimming_enabled"] = True
                if "auto_accept_enabled" not in self.data:  
                    self.data["auto_accept_enabled"] = True
                self.save_settings()
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = self.DEFAULT_SETTINGS
            self.save_settings()

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.data, f, indent=4)

def apply_theme_to_titlebar(root):
    version = sys.getwindowsversion()

    if version.major == 10 and version.build >= 22000:
        # Set the title bar color to the background color on Windows 11 for better appearance
        pywinstyles.change_header_color(root, "#1c1c1c" if sv_ttk.get_theme() == "dark" else "#fafafa")
    elif version.major == 10:
        pywinstyles.apply_style(root, "dark" if sv_ttk.get_theme() == "dark" else "normal")

        # A hacky way to update the title bar's color on Windows 10 (it doesn't update instantly like on Windows 11)
        root.wm_attributes("-alpha", 0.99)
        root.wm_attributes("-alpha", 1)

class SettingsWindow:
    def __init__(self, settings):
        self.settings = settings
        self.root = tk.Tk()
        self.root.title("QOL Settings")
        self.root.geometry("400x700")  # Reduced initial window size
        sv_ttk.set_theme(darkdetect.theme())
        self.monitor_vars = {}
        self.monitor_ids = {}  # Store mapping of display name to ID
        self.create_widgets()
        apply_theme_to_titlebar(self.root)  # Apply title bar theme

    def get_running_programs(self):
        """Get list of running program window titles"""
        programs = set()
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and len(title) > 1:  # Filter out empty or single char titles
                    programs.add(title)
        win32gui.EnumWindows(enum_windows_callback, None)
        return sorted(list(programs))

    def refresh_running_programs(self):
        """Refresh the list of running programs"""
        self.running_list.delete(0, tk.END)
        for program in self.get_running_programs():
            self.running_list.insert(tk.END, program)

    def create_unique_monitor_id(self, info):
        """Create a unique monitor ID from monitor properties"""
        # Use the 'serial' property if available, otherwise fall back to other properties
        monitor_properties = [
            str(info.get('serial', '')),
            str(info.get('name', '')),
            str(info.get('manufacturer', '')),
            str(info.get('index', ''))  
        ]
        return "|".join(filter(None, monitor_properties))

    def create_widgets(self):
        # Main container with vertical layout
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Top section for monitors and brightness
        top_section = ttk.Frame(main_container)
        top_section.pack(fill="x", expand=False)

        # Monitors Frame
        monitors_frame = ttk.LabelFrame(top_section, text="Dimmable Monitors", padding=10)
        monitors_frame.pack(fill="x", pady=(0, 5))
        
        try:
            monitors_info = sbc.list_monitors_info()
            logger.debug(f"Found {len(monitors_info)} monitors")
            
            # Print all monitor data
            for info in monitors_info:
                logger.debug(f"Monitor data: {info}")
            
            # Create checkbox for each monitor with unique ID
            for index, info in enumerate(monitors_info):
                # Create unique ID from monitor properties
                monitor_id = self.create_unique_monitor_id(info)
                serial = info.get('serial', 'Unknown')
                name = info.get('name', 'Unknown')
                
                display_name = (
                    f"Monitor {index + 1}: {name}"
                )
                
                logger.debug(f"Adding monitor: {display_name} with ID: {monitor_id}")
                
                var = tk.BooleanVar()
                var.set(serial in self.settings.data["dimmable_monitors"])
                
                self.monitor_vars[serial] = var
                self.monitor_ids[display_name] = serial
                
                frame = ttk.Frame(monitors_frame)
                frame.pack(fill="x", pady=5)
                
                ttk.Checkbutton(
                    frame, 
                    text=display_name,
                    variable=var
                ).pack(anchor="w")

        except Exception as e:
            logger.error(f"Error setting up monitor checkboxes: {e}")
            # Add a label to show the error
            ttk.Label(
                monitors_frame,
                text=f"Error loading monitors: {str(e)}",
                foreground="red"
            ).pack(fill="x", pady=5)

        # Brightness Frame
        brightness_frame = ttk.LabelFrame(top_section, text="Brightness Settings", padding=10)
        brightness_frame.pack(fill="x", pady=5)
        
        ttk.Label(brightness_frame, text="High:").pack()
        self.high_brightness = tk.Scale(brightness_frame, from_=0, to=100, orient="horizontal")
        self.high_brightness.set(self.settings.data["monitor_brightness"]["high"])
        self.high_brightness.pack(fill="x")
        
        ttk.Label(brightness_frame, text="Low:").pack()
        self.low_brightness = tk.Scale(brightness_frame, from_=0, to=100, orient="horizontal")
        self.low_brightness.set(self.settings.data["monitor_brightness"]["low"])
        self.low_brightness.pack(fill="x")

        # Games section
        games_section = ttk.Frame(main_container)
        games_section.pack(fill="both", expand=True, pady=5)

        # Games to Dim
        games_frame = ttk.LabelFrame(games_section, text="Games to Dim", padding=10)
        games_frame.pack(fill="both", expand=True)
        
        self.games_text = tk.Text(games_frame, height=5)  # Reduced height
        self.games_text.pack(fill="both", expand=True)
        self.games_text.insert("1.0", "\n".join(self.settings.data["games_to_dimm"]))

        # Running Programs (bottom section, initially hidden)
        running_section = ttk.Frame(main_container)
        running_section.pack(fill="x", expand=False, pady=5)
        
        running_frame = ttk.LabelFrame(running_section, text="Running Programs", padding=10)
        running_frame.pack(fill="x")
        
        list_frame = ttk.Frame(running_frame)
        list_frame.pack(fill="x")
        
        self.running_list = tk.Listbox(list_frame, height=6)  # Reduced height
        self.running_list.pack(side="left", fill="x", expand=True)
        
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(side="right", padx=5)
        
        ttk.Label(
            button_frame,
            text="Double-click to add",
            font=("", 8)  # Smaller font
        ).pack()
        
        ttk.Button(
            button_frame,
            text="Refresh List",
            command=self.refresh_running_programs  # Now this method exists
        ).pack(pady=5)

        # Populate running programs
        for program in self.get_running_programs():
            self.running_list.insert(tk.END, program)
        
        def on_double_click(event):
            selection = self.running_list.curselection()
            if selection:
                program = self.running_list.get(selection[0])
                self.games_text.insert(tk.END, f"\n{program}")
        
        self.running_list.bind('<Double-Button-1>', on_double_click)

        # Save Button at bottom
        save_frame = ttk.Frame(self.root)
        save_frame.pack(fill="x", pady=10, padx=10)
        ttk.Button(
            save_frame,
            text="Save",
            command=self.save_settings
        ).pack(side="right")

    def toggle_running_programs(self):
        """Toggle the visibility of the running programs section"""
        if self.root.winfo_height() == 400:
            self.root.geometry("800x600")
        else:
            self.root.geometry("800x400")

    def save_settings(self):
        """Save current settings and close window"""
        try:
            # Log current state before saving
            logger.debug(f"Current monitor vars: {self.monitor_vars}")
            
            # Save selected monitor serials
            selected_monitors = [
                serial for serial, var in self.monitor_vars.items() 
                if var.get()
            ]
            logger.debug(f"Saving selected monitors: {selected_monitors}")
            self.settings.data["dimmable_monitors"] = selected_monitors

            # Save brightness values
            self.settings.data["monitor_brightness"]["high"] = self.high_brightness.get()
            self.settings.data["monitor_brightness"]["low"] = self.low_brightness.get()

            # Save games list
            self.settings.data["games_to_dimm"] = [
                x.strip() for x in self.games_text.get("1.0", "end-1c").split("\n") 
                if x.strip()
            ]

            # Save to file and close window
            self.settings.save_settings()
            self.root.destroy()
        except Exception as e:
            logger.error(f"Error saving settings: {e}")

class AutoAccept:
    def __init__(self):
        self.settings = Settings()
        self.create_tray_icon()
        self.running = True
        # Add signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        logger.debug("Received signal to terminate. Cleaning up...")
        self.stop()

    def create_tray_icon(self):
        icon_image = Image.new('RGB', (64, 64), color='red')
        
        def check_dimming(item):
            return self.settings.data["dimming_enabled"]
        
        def check_auto_accept(item):
            return self.settings.data["auto_accept_enabled"]
        
        def toggle_dimming(icon, item):
            self.settings.data["dimming_enabled"] = not self.settings.data["dimming_enabled"]
            self.settings.save_settings()
            if not self.settings.data["dimming_enabled"]:
                set_brigtness_side_monitors(
                    self.settings.data["monitor_brightness"]["high"],
                    self.settings.data["dimmable_monitors"]
                )

        def toggle_auto_accept(icon, item):
            self.settings.data["auto_accept_enabled"] = not self.settings.data["auto_accept_enabled"]
            self.settings.save_settings()

        def open_about(icon, item):
            webbrowser.open("https://github.com/ExampleUser/ExampleRepo")

        menu_items = [
            pystray.MenuItem(PROGRAM_NAME, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Auto Accept",
                toggle_auto_accept,
                checked=check_auto_accept
            ),
            pystray.MenuItem(
                "Dimming",
                toggle_dimming,
                checked=check_dimming
            ),
            pystray.MenuItem("Settings", self.show_settings),
            pystray.MenuItem("About", open_about),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.stop)
        ]

        menu = pystray.Menu(*menu_items)

        self.icon = pystray.Icon(
            PROGRAM_NAME,
            icon_image,
            PROGRAM_NAME,
            menu=menu
        )

    def show_settings(self):
        settings_window = SettingsWindow(self.settings)
        settings_window.root.mainloop()

    def stop(self):
        if self.running:
            self.running = False
            self.icon.stop()
            # Ensure brightness is restored before exit
            if self.settings.data["dimming_enabled"]:
                set_brigtness_side_monitors(
                    self.settings.data["monitor_brightness"]["high"],
                    self.settings.data["dimmable_monitors"]
                )

    def run(self):
        Thread(target=self.main_loop).start()
        self.icon.run()

    def main_loop(self):
        while self.running:
            # Only check for matches if auto accept is enabled
            if self.settings.data["auto_accept_enabled"]:
                if league_client_is_open():
                    try:
                        accept_lol_via_lcu()
                    except Exception as e:
                        logger.exception("Error while attempting to accept LoL match via LCU.")

                foregroundWindow = GetForegroundWindow()
                focused = GetWindowText(foregroundWindow)

                if "Counter-Strike" in focused:
                    accept_match(encoded_accept_cs)

            # Handle dimming separately
            if self.settings.data["dimming_enabled"]:
                focused = GetWindowText(GetForegroundWindow())
                if focused in self.settings.data['games_to_dimm']:
                    set_brigtness_side_monitors(
                        self.settings.data["monitor_brightness"]["low"],
                        self.settings.data["dimmable_monitors"]
                    )
                else:
                    set_brigtness_side_monitors(
                        self.settings.data["monitor_brightness"]["high"],
                        self.settings.data["dimmable_monitors"]
                    )

            time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QOL-Scripts")
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    logger = setup_logging(args.debug)

    app = AutoAccept()
    try:
        app.run()
    except KeyboardInterrupt:
        logger.debug("Received Ctrl+C. Shutting down...")
        app.stop()
