# Anti-WorkCat 😾 ("Nee thurakku... njan adakkam")

[![TinkerHub Useless Projects 3.0](https://img.shields.io/badge/TinkerHub-UselessProjects3.0-orange?style=for-the-badge)](https://tinkerhub.org)

> The ultimate anti-productivity desktop pet cat. While apps like WorkCat try to keep you focused, **Anti-WorkCat** has one goal: **destroy your productivity and force you to scroll Reels**.

---

## 🎯 Basic Details

### Team Name: TechHack
### Team Members
- **Team Lead**: Vaishnavi P B — LBSITW
- **Member 2**: Harsha Hari — LBSITW

---

## 💡 Project Description
Anti-WorkCat is a mischievous, roaming desktop pet cat built as the exact opposite of WorkCat. Whenever you open a productive application like **VS Code, Visual Studio, or Terminal**, the cat gets visibly irritated, walks across your screen, and **smashes the window closed (WM_CLOSE)** while giving hilarious Manglish commentary. Meanwhile, opening Instagram, Reels, or Netflix makes the cat sit down happily and encourage your procrastination.

### ❌ The Problem (that doesn't exist)
People are working *way* too hard. Society is overloaded with focus timers, pomodoro apps, and productivity trackers. Nobody is taking enough time to scroll Instagram Reels or binge Netflix.

### 😼 The Solution (that nobody asked for)
An aggressive, zero-patience desktop pet cat that:
1. **Monitors your active windows** in real-time.
2. **Gets irritated** when you attempt to write code or open terminals.
3. **Marches over to VS Code** and uses its front paw to smash the window closed.
4. **Encourages bad habits** with iconic Manglish dialogues like *"Nee thurakku... njan adakkam"* and *"Oru reel koodi"*.

---

## 🗣️ Iconic Manglish Dialogues

| Trigger | Cat Reaction / Speech Bubble |
| :--- | :--- |
| **😾 Productive App Opened** | *"Ayyo… veendum work aano?"* / *"Nee thurakku… njan adakkam."* / *"Ithu venda."* |
| **🚶 Cat Walking to Close** | *"Njan varunnund…"* / *"Nice try."* / *"Odi rakshappedanda."* |
| **🐾 After Closing Window** | *"Aah… ippo correct."* / *"Problem solved."* / *"You’re welcome."* |
| **📱 Instagram / Reels** | *"Ithaanu nammade vazhi."* / *"Oru reel koodi."* / *"Aah… ippo samadhanam."* |
| **🎬 Netflix / YouTube** | *"Just one episode."* / *"Work pinne cheyyaam."* / *"Now we’re talking."* |
| **🔁 Productivity Reopened** | *"Ayyo… pinneyum?"* / *"Nee enne test cheyyuvaano?"* / *"Ithu ippo personal aanu."* |

---

## 🛠️ Technical Details

### Technologies Used
- **Python 3**: Native Windows Desktop Pet (`tkinter` transparent overlay + `ctypes` Win32 API).
- **Win32 API (`user32.dll`)**: Foreground window handle detection, window bounds geometry, and `WM_CLOSE` window destruction.
- **Pillow (PIL)**: Custom pixel art sprite rendering (Orange Calico Cat).
- **HTML5 / CSS3 / JavaScript (ES6+)**: Interactive Web Desktop Simulator & Hackathon Showcase Page.
- **Web Audio API**: Synthesized cat meows and paw smash thuds.

---

## 🚀 How to Run

### 1. Web Interactive Simulator
Simply open `index.html` in any browser to test the cat in a simulated desktop environment with draggable VS Code, Instagram, and Netflix windows!

### 2. Native Windows Desktop Pet
To run the cat natively on your Windows computer:

```bash
# 1. Clone the repository & navigate to directory
git clone https://github.com/int-main-vaish/useless_project_temp.0.git
cd useless_project_temp

# 2. Generate Pixel Cat Sprites
python generate_assets.py

# 3. Run the Desktop Pet!
python anti_workcat.py
```

---

## 👥 Team Contributions
- **Vaishnavi P B**: Concept design, Win32 API integration, Python desktop pet development, and state machine logic.
- **Harsha Hari**: Web simulator development, UI/UX glassmorphic design, sprite generation, and dialogue soundboard.

---
Made with ❤️ at **TinkerHub Useless Projects 3.0**