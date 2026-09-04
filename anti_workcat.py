import os
import sys
import time
import random
import ctypes
from ctypes import wintypes
import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import uiautomation as auto
import winsound
import threading

def play_meow_sound():
    """Plays the uploaded cat meow audio file (sound/meow.mp3) asynchronously when cat giggles."""
    def _meow():
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            sound_path = os.path.join(base_dir, "sound", "meow.mp3")
            if os.path.exists(sound_path):
                winmm = ctypes.windll.winmm
                winmm.mciSendStringW("close meow_sound", None, 0, 0)
                winmm.mciSendStringW(f'open "{sound_path}" type mpegvideo alias meow_sound', None, 0, 0)
                winmm.mciSendStringW("play meow_sound from 0", None, 0, 0)
            else:
                winsound.Beep(440, 90)
                winsound.Beep(659, 140)
                winsound.Beep(587, 100)
        except Exception:
            pass
    threading.Thread(target=_meow, daemon=True).start()

auto.SetGlobalSearchTimeout(0.5)

# --- Win32 API Definitions & DPI Awareness ---
user32 = ctypes.windll.user32

try:
    user32.SetProcessDPIAware()
except Exception:
    pass

WM_CLOSE = 0x0010

# --- Win32 Focus & Keyboard API Definitions ---
VK_CONTROL = 0x11
VK_W = 0x57
KEYEVENTF_KEYUP = 0x0002

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]

user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
user32.GetWindowRect.restype = wintypes.BOOL
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostMessageW.restype = wintypes.BOOL
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
user32.AttachThreadInput.restype = wintypes.BOOL
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL
user32.BringWindowToTop.argtypes = [wintypes.HWND]
user32.BringWindowToTop.restype = wintypes.BOOL
user32.keybd_event.argtypes = [wintypes.BYTE, wintypes.BYTE, wintypes.DWORD, ctypes.c_size_t]

def force_foreground(hwnd):
    """Forcefully bring target window to foreground even if caller is background."""
    if not hwnd:
        return False
    
    current_fg = user32.GetForegroundWindow()
    if current_fg == hwnd:
        return True
        
    fg_thread = user32.GetWindowThreadProcessId(current_fg, None)
    target_thread = user32.GetWindowThreadProcessId(hwnd, None)
    
    if fg_thread and target_thread and fg_thread != target_thread:
        user32.AttachThreadInput(fg_thread, target_thread, True)
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        user32.SetForegroundWindow(hwnd)
        user32.BringWindowToTop(hwnd)
        user32.AttachThreadInput(fg_thread, target_thread, False)
    else:
        user32.ShowWindow(hwnd, 9)
        user32.SetForegroundWindow(hwnd)
        user32.BringWindowToTop(hwnd)
        
    time.sleep(0.1)
    return user32.GetForegroundWindow() == hwnd

def get_active_window_info():
    """Returns (hwnd, title, (left, top, right, bottom)) of active foreground window."""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None, "", (0, 0, 0, 0)
    
    length = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    
    return hwnd, buf.value, (rect.left, rect.top, rect.right, rect.bottom)

def close_window(hwnd):
    """Sends WM_CLOSE message to target window handle (closes whole app)."""
    if hwnd:
        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)

def close_browser_tab(hwnd):
    """Brings browser to foreground and sends Ctrl+W to close only the active tab."""
    if not hwnd:
        return
        
    # Force browser into active focus
    force_foreground(hwnd)
    time.sleep(0.15)
    
    # Send Ctrl+W key combination using Win32 keybd_event
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_W, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_W, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

# Browser process identifiers — matched against window title
BROWSER_KEYWORDS = [
    "google chrome", "chrome", "mozilla firefox", "firefox",
    "microsoft edge", "edge", "opera", "brave", "vivaldi", "arc",
]

def get_browser_tab_rect(hwnd, title):
    """Finds exact screen rectangle (left, top, right, bottom) of the productive tab item using UI Automation."""
    try:
        win_control = auto.ControlFromHandle(hwnd)
        if not win_control:
            return None
            
        title_lower = (title or "").lower()
        selected_rect = None
        keyword_rect = None
        
        for control, depth in auto.WalkControl(win_control, maxDepth=8):
            if control.ControlTypeName == 'TabItemControl':
                tab_name = (control.Name or "").lower()
                rect = control.BoundingRectangle
                
                # Ensure valid rect on screen
                if rect.right <= rect.left or rect.bottom <= rect.top:
                    continue
                
                # Check exact title match
                if tab_name and (tab_name in title_lower or title_lower.startswith(tab_name)):
                    return (rect.left, rect.top, rect.right, rect.bottom)
                
                # Check productive keyword match in tab title
                if any(kw in tab_name for kw in PRODUCTIVE_KEYWORDS):
                    keyword_rect = (rect.left, rect.top, rect.right, rect.bottom)
                    
                # Store selected tab fallback
                try:
                    if getattr(control, 'IsSelected', False) or getattr(control, 'HasKeyboardFocus', False):
                        selected_rect = (rect.left, rect.top, rect.right, rect.bottom)
                except Exception:
                    pass

        return keyword_rect or selected_rect
    except Exception:
        return None

# --- Dialogues & Configuration ---
DIALOGUES = {
    "PRODUCTIVE_OPENED": [
        "Dont Play with me Nigeshhhh 😾",
        "Nee thurakku… njan adakkam.",
        "Vendatta Venda 🚫"
    ],
    "GOING_TO_CLOSE": [
        "Vannu njann 🚶🐾",
        "Nice try. 😏",
    ],
    "AFTER_CLOSING": [
        "Aah… ippo correct. ✨",
        "Problem solved. 😼",
        "You’re welcome. 💅"
    ],
    "INSTAGRAM_OPENED": [
        "Ada Gommale",
        "Oru reel kude kanaam 🙂↕️ 🎬",
        "Ingane Ingane cheyy Baalu 💖"
    ],
    "NETFLIX_OPENED": [
        "Now we’re talking netflix. 😎",
        "Just one episode. 🍿",
        "Work pinne cheyyaam. 💤",
    ],
    "REOPENED_PRODUCTIVE": [
        "Ayyo… pinneyum? 💢",
        "Ithu ippo personal aanu. 🔥😾"
    ],
    "SIGNATURE": [
        "Nee thurakku… njan adakkam.",
        "Poda kochu cherukka",
        "Same mistake, different app."
    ],
    "GIGGLE": [
        "Hehehe… tickles! 😸✨",
        "Kili kili! 😸",
        "happy happy happyy 😸💖",
        "Enthaappa ithu? 😸"
    ],
    "SLEEP": [
        "Zzz... 💤",
        "Sshh... njan uranguva 😴",
        "Night night 💤"
    ]
}

PRODUCTIVE_KEYWORDS = [
    # IDEs & Code Editors
    "visual studio", "vs code", "code", "sublime", "pycharm", "intellij",
    "eclipse", "cursor", "cursor ai", "android studio", "atom", "vim", "neovim",
    # Terminals & Shells
    "terminal", "powershell", "cmd", "command prompt", "windows terminal",
    # Coding / Competitive Programming Websites (browser tab titles)
    "geeksforgeeks", "geeks for geeks", "leetcode", "hackerrank", "hacker rank",
    "codechef", "codeforces", "topcoder", "codewars", "exercism",
    "w3schools", "stackoverflow", "stack overflow", "github", "gitlab", "bitbucket",
    # AI Assistants (study / coding help)
    "claude", "claude ai", "chatgpt", "chat gpt", "openai", "gemini", "copilot",
    "perplexity", "bard",
    # PDF / Documents in browser or reader
    ".pdf", "pdf", "adobe acrobat", "acrobat reader", "foxit",
    # Office & Productivity Apps
    "overleaf", "word", "excel", "powerpoint", "notion", "figma",
    "google docs", "google sheets", "google slides",
    # Study / Learning Platforms
    "coursera", "udemy", "edx", "khan academy", "codecademy", "freecodecamp",
    "brilliant", "mit opencourseware", "nptel",
]

DISTRACTION_KEYWORDS = [
    "instagram", "facebook", "reels", "shorts", "tiktok", "netflix", "youtube", "reddit"
]

def is_browser_window(title):
    """Check if a window title belongs to a web browser."""
    title_lower = title.lower()
    return any(bk in title_lower for bk in BROWSER_KEYWORDS)

class AntiWorkCatApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AntiWorkCat - Desktop Pet")
        
        # Transparent, Frameless, Always-On-Top Setup
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "green")
        
        # Get Screen Dimensions
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        
        # Initial Position (Bottom right of desktop, fully inside screen bounds)
        self.cat_x = max(10, self.screen_w - 360)
        self.cat_y = max(10, self.screen_h - 260)
        self.root.geometry(f"320x180+{int(self.cat_x)}+{int(self.cat_y)}")
        
        # Canvas Layout
        self.canvas = tk.Canvas(self.root, width=320, height=180, bg="green", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Load Sprites
        self.sprites = {}
        self.load_sprites()
        
        # Speech Bubble & Cat Image Objects
        self.bubble_rect = self.canvas.create_rectangle(10, 10, 310, 60, fill="#1e1e2e", outline="#f58c32", width=2, state="hidden")
        self.bubble_text = self.canvas.create_text(160, 35, text="", fill="#ffffff", font=("Segoe UI", 10, "bold"), width=290, justify="center", state="hidden")
        self.cat_img_id = self.canvas.create_image(160, 120, image=self.sprites.get("idle_right"))
        
        # Make Cat Draggable & Clickable for Giggle
        self.canvas.tag_bind(self.cat_img_id, "<ButtonPress-1>", self.on_cat_click)
        self.canvas.tag_bind(self.cat_img_id, "<B1-Motion>", self.on_drag_motion)
        
        # State Machine Variables
        self.state = "IDLE"  # IDLE, IRRITATED, WALKING_TO_CLOSE, SMASHING, HAPPY, SLEEPING, GIGGLING
        self.idle_start_time = time.time()
        self.facing = "right" # left or right
        self.walk_step = 0
        self.target_hwnd = None
        self.target_close_pos = (0, 0)
        self.target_is_browser = False
        self.last_closed_hwnd = None
        self.reopen_count = 0
        self.bubble_clear_timer = None
        
        # Start Loops
        self.root.after(30, self.update_loop)
        self.root.after(1200, self.check_active_window)

    def load_sprites(self):
        sprite_files = {
            "idle": "cat_idle.png",
            "walk1": "cat_walk1.png",
            "walk2": "cat_walk2.png",
            "sit": "cat_sit.png",
            "angry": "cat_angry.png",
            "smash": "cat_smash.png",
            "sleep": "cat_sleep.png",
            "giggle": "cat_giggle.png"
        }
        
        for key, fname in sprite_files.items():
            path = os.path.join("sprites", fname)
            if os.path.exists(path):
                img_right = Image.open(path).resize((96, 96), Image.Resampling.NEAREST)
                img_left = ImageOps.mirror(img_right)
                
                self.sprites[f"{key}_right"] = ImageTk.PhotoImage(img_right)
                self.sprites[f"{key}_left"] = ImageTk.PhotoImage(img_left)
            else:
                img = Image.new("RGBA", (96, 96), (245, 140, 50, 255))
                self.sprites[f"{key}_right"] = ImageTk.PhotoImage(img)
                self.sprites[f"{key}_left"] = ImageTk.PhotoImage(img)

    def speak(self, text, duration_ms=3500):
        self.canvas.itemconfig(self.bubble_text, text=text, state="normal")
        self.canvas.itemconfig(self.bubble_rect, state="normal")
        if self.bubble_clear_timer:
            self.root.after_cancel(self.bubble_clear_timer)
        self.bubble_clear_timer = self.root.after(duration_ms, self.hide_speech)

    def hide_speech(self):
        self.canvas.itemconfig(self.bubble_text, state="hidden")
        self.canvas.itemconfig(self.bubble_rect, state="hidden")

    def set_sprite(self, pose_key):
        full_key = f"{pose_key}_{self.facing}"
        if full_key in self.sprites:
            self.canvas.itemconfig(self.cat_img_id, image=self.sprites[full_key])

    def on_cat_click(self, event):
        self._drag_start_x = event.x_root - self.cat_x
        self._drag_start_y = event.y_root - self.cat_y
        
        # Trigger giggle reaction with meow audio when clicked
        if self.state in ["IDLE", "SLEEPING", "HAPPY"]:
            self.state = "GIGGLING"
            self.set_sprite("giggle")
            play_meow_sound()
            self.speak(random.choice(DIALOGUES["GIGGLE"]), 2000)
            self.root.after(2000, self.reset_to_idle)

    def on_drag_motion(self, event):
        self.cat_x = event.x_root - self._drag_start_x
        self.cat_y = event.y_root - self._drag_start_y
        self.root.geometry(f"320x180+{int(self.cat_x)}+{int(self.cat_y)}")
        self.idle_start_time = time.time()

    def check_active_window(self):
        if self.state in ["WALKING_TO_CLOSE", "SMASHING"]:
            self.root.after(1000, self.check_active_window)
            return

        hwnd, title, (left, top, right, bottom) = get_active_window_info()
        title_lower = title.lower()

        if hwnd and title != "AntiWorkCat - Desktop Pet":
            is_productive = any(kw in title_lower for kw in PRODUCTIVE_KEYWORDS)
            is_distraction = any(kw in title_lower for kw in DISTRACTION_KEYWORDS)

            if is_productive:
                if hwnd == self.last_closed_hwnd:
                    self.reopen_count += 1
                    quote_cat = "REOPENED_PRODUCTIVE"
                else:
                    self.reopen_count = 0
                    quote_cat = "PRODUCTIVE_OPENED"

                self.target_hwnd = hwnd
                self.target_is_browser = is_browser_window(title)
                
                tab_rect = None
                if self.target_is_browser:
                    tab_rect = get_browser_tab_rect(hwnd, title)
                    
                if tab_rect:
                    t_left, t_top, t_right, t_bottom = tab_rect
                    tab_center_x = t_left + (t_right - t_left) // 2
                    # Direct cat to the exact center of the active productive tab on screen!
                    target_x = max(10, min(self.screen_w - 320, tab_center_x - 160))
                    target_y = max(10, min(self.screen_h - 180, t_top - 40))
                elif self.target_is_browser:
                    # Fallback for browser top bar
                    target_x = max(10, min(self.screen_w - 320, left + 150))
                    target_y = max(10, min(self.screen_h - 180, top - 40))
                else:
                    # Target top-right window close button for desktop apps
                    target_x = max(10, min(self.screen_w - 320, right - 160))
                    target_y = max(10, min(self.screen_h - 180, top - 40))
                    
                self.target_close_pos = (target_x, target_y)
                
                # Face direction of target
                self.facing = "left" if self.target_close_pos[0] < self.cat_x else "right"
                
                self.state = "IRRITATED"
                self.set_sprite("angry")
                self.speak(random.choice(DIALOGUES[quote_cat]))
                
                self.root.after(800, self.start_walking_to_close)

            elif is_distraction and self.state != "HAPPY":
                self.state = "HAPPY"
                self.set_sprite("sit")
                if "netflix" in title_lower or "youtube" in title_lower:
                    self.speak(random.choice(DIALOGUES["NETFLIX_OPENED"]))
                else:
                    self.speak(random.choice(DIALOGUES["INSTAGRAM_OPENED"]))
                self.root.after(4000, self.reset_to_idle)

        self.root.after(1200, self.check_active_window)

    def start_walking_to_close(self):
        self.state = "WALKING_TO_CLOSE"
        self.walk_step = 0
        self.speak(random.choice(DIALOGUES["GOING_TO_CLOSE"]))

    def update_loop(self):
        if self.state == "WALKING_TO_CLOSE":
            tx, ty = self.target_close_pos
            dx = tx - self.cat_x
            dy = ty - self.cat_y
            dist = (dx**2 + dy**2) ** 0.5

            # Update facing direction
            self.facing = "left" if dx < 0 else "right"

            if dist < 25:
                # Reached close button! Smash!
                self.state = "SMASHING"
                self.set_sprite("smash")
                self.speak("Bleh ;)")
                self.root.after(450, self.execute_smash)
            else:
                # Smooth movement step (6px per tick)
                speed = min(12, max(4, dist / 12))
                self.cat_x += (dx / dist) * speed
                self.cat_y += (dy / dist) * speed
                self.root.geometry(f"320x180+{int(self.cat_x)}+{int(self.cat_y)}")
                
                # Alternate leg walking animation every 4 frames (~120ms)
                self.walk_step += 1
                walk_pose = "walk1" if (self.walk_step // 4) % 2 == 0 else "walk2"
                self.set_sprite(walk_pose)

        elif self.state == "IDLE":
            # If idle for more than 2 seconds, cat goes to sleep
            if time.time() - self.idle_start_time >= 2.0:
                self.state = "SLEEPING"
                self.set_sprite("sleep")
                self.speak(random.choice(DIALOGUES["SLEEP"]), 4000)
            elif random.random() < 0.03:
                step_x = random.choice([-8, 8])
                self.facing = "left" if step_x < 0 else "right"
                self.cat_x = max(20, min(self.screen_w - 340, self.cat_x + step_x))
                self.cat_y = max(50, min(self.screen_h - 220, self.cat_y + random.choice([-2, 2])))
                self.root.geometry(f"320x180+{int(self.cat_x)}+{int(self.cat_y)}")
                self.set_sprite("idle")

        self.root.after(30, self.update_loop)

    def execute_smash(self):
        if self.target_hwnd:
            if self.target_is_browser:
                # Close only the active browser tab (Ctrl+W)
                close_browser_tab(self.target_hwnd)
            else:
                # Close the whole app window
                close_window(self.target_hwnd)
            self.last_closed_hwnd = self.target_hwnd
            self.target_hwnd = None
            self.target_is_browser = False
            
        self.set_sprite("idle")
        self.speak(random.choice(DIALOGUES["AFTER_CLOSING"]))
        self.root.after(3000, self.reset_to_idle)

    def reset_to_idle(self):
        self.state = "IDLE"
        self.idle_start_time = time.time()
        self.set_sprite("idle")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AntiWorkCatApp()
    app.run()