import os
import sys
import time
import random
import ctypes
from ctypes import wintypes
import tkinter as tk
from PIL import Image, ImageTk, ImageOps

# --- Win32 API Definitions & DPI Awareness ---
user32 = ctypes.windll.user32

try:
    user32.SetProcessDPIAware()
except Exception:
    pass

WM_CLOSE = 0x0010

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
    """Sends WM_CLOSE message to target window handle."""
    if hwnd:
        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)

# --- Dialogues & Configuration ---
DIALOGUES = {
    "PRODUCTIVE_OPENED": [
        "Ayyo… veendum work aano? 😾",
        "Nee thurakku… njan adakkam.",
        "Ithu venda. 🚫"
    ],
    "GOING_TO_CLOSE": [
        "Njan varunnund… 🚶🐾",
        "Nice try. 😏",
        "Odi rakshappedanda. 🔥"
    ],
    "AFTER_CLOSING": [
        "Aah… ippo correct. ✨",
        "Problem solved. 😼",
        "You’re welcome. 💅"
    ],
    "INSTAGRAM_OPENED": [
        "Ithaanu nammade vazhi. 📱",
        "Oru reel koodi. 🎬",
        "Aah… ippo samadhanam. 💖"
    ],
    "NETFLIX_OPENED": [
        "Just one episode. 🍿",
        "Work pinne cheyyaam. 💤",
        "Now we’re talking. 😎"
    ],
    "REOPENED_PRODUCTIVE": [
        "Ayyo… pinneyum? 💢",
        "Nee enne test cheyyuvaano?",
        "Ithu ippo personal aanu. 🔥😾"
    ],
    "SIGNATURE": [
        "Nee thurakku… njan adakkam.",
        "Ippo vannallo vazhikku.",
        "Same mistake, different app."
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
        
        # Initial Position (Bottom right of desktop)
        self.cat_x = self.screen_w - 200
        self.cat_y = self.screen_h - 220
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
        
        # Make Cat Draggable by Mouse
        self.canvas.tag_bind(self.cat_img_id, "<ButtonPress-1>", self.on_drag_start)
        self.canvas.tag_bind(self.cat_img_id, "<B1-Motion>", self.on_drag_motion)
        
        # State Machine Variables
        self.state = "IDLE"  # IDLE, IRRITATED, WALKING_TO_CLOSE, SMASHING, HAPPY
        self.facing = "right" # left or right
        self.walk_step = 0
        self.target_hwnd = None
        self.target_close_pos = (0, 0)
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
            "smash": "cat_smash.png"
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

    def on_drag_start(self, event):
        self._drag_start_x = event.x_root - self.cat_x
        self._drag_start_y = event.y_root - self.cat_y

    def on_drag_motion(self, event):
        self.cat_x = event.x_root - self._drag_start_x
        self.cat_y = event.y_root - self._drag_start_y
        self.root.geometry(f"320x180+{int(self.cat_x)}+{int(self.cat_y)}")

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
                self.target_close_pos = (
                    max(10, min(self.screen_w - 320, right - 160)),
                    max(10, min(self.screen_h - 180, top - 40))
                )
                
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
                self.speak("PAW SMASH! 💥🐾")
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
            if random.random() < 0.03:
                step_x = random.choice([-8, 8])
                self.facing = "left" if step_x < 0 else "right"
                self.cat_x = max(20, min(self.screen_w - 340, self.cat_x + step_x))
                self.cat_y = max(50, min(self.screen_h - 220, self.cat_y + random.choice([-2, 2])))
                self.root.geometry(f"320x180+{int(self.cat_x)}+{int(self.cat_y)}")
                self.set_sprite("idle")
                self.set_sprite("idle")

        self.root.after(30, self.update_loop)

    def execute_smash(self):
        if self.target_hwnd:
            close_window(self.target_hwnd)
            self.last_closed_hwnd = self.target_hwnd
            self.target_hwnd = None
            
        self.set_sprite("idle")
        self.speak(random.choice(DIALOGUES["AFTER_CLOSING"]))
        self.root.after(3000, self.reset_to_idle)

    def reset_to_idle(self):
        self.state = "IDLE"
        self.set_sprite("idle")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AntiWorkCatApp()
    app.run()