import pyautogui
import time
import urllib.request
import keyboard
import screen_brightness_control as sbc
from win32gui import GetWindowText, GetForegroundWindow
from win32con import WM_INPUTLANGCHANGEREQUEST
from win32api import SendMessage

# Accept images
urllib.request.urlretrieve("https://i.imgur.com/0UPHbGX.png", "cs_accept_image.png")
urllib.request.urlretrieve("https://raw.githubusercontent.com/matiasperz/lol-auto-accept/master/sample.png", "lol_accept_image.png")

# Toggle variable
gamming_dimm = False

def set_brigtness_side_monitors(brightness):
    sbc.set_brightness(brightness, display=1)
    sbc.set_brightness(brightness, display=2)

def accept_match(game):
    try:
        accept_btn = pyautogui.locateCenterOnScreen(f"{game}_accept_image.png", confidence=0.8)
        if accept_btn != None:
            pyautogui.click(accept_btn)
    except:
        print("Accept error")

def toggle_var():
    global gamming_dimm
    gamming_dimm = not gamming_dimm

keyboard.add_hotkey('windows + F9', toggle_var)

while True:

    # Accept match and monitor brightness per game
    foregroundWindow = GetForegroundWindow()
    focused = GetWindowText(foregroundWindow)
    # print(focused)

    if focused in ["Counter-Strike: Global Offensive - Direct3D 9", "League of Legends (TM) Client", "League of Legends", "EscapeFromTarkov"] or gamming_dimm:
        match focused:
            case "League of Legends":
                accept_match("lol")

            case "League of Legends (TM) Client":
                set_brigtness_side_monitors(20)

            case "Counter-Strike: Global Offensive - Direct3D 9":
                set_brigtness_side_monitors(20)
                accept_match("cs")
                try:
                    SendMessage(foregroundWindow, WM_INPUTLANGCHANGEREQUEST, 0, 0x0000409)
                except:
                    print("An has occurred in line 58")


            case "EscapeFromTarkov":
                set_brigtness_side_monitors(10)

            case _:
                set_brigtness_side_monitors(20)
    else:
        try:
            SendMessage(GetForegroundWindow(), WM_INPUTLANGCHANGEREQUEST, 0, 0x00020409)
        except:
            print("An has occurred in line 69")

        set_brigtness_side_monitors(100)

    time.sleep(0.2)
