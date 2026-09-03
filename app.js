// Anti-WorkCat Interactive Web Desktop Simulator & Audio Engine

const DIALOGUES = {
    PRODUCTIVE_OPENED: [
        "Dont Play with me Nigeshhhh 😾",
        "Nee thurakku… njan adakkam.",
        "Vendatta Venda 🚫"
    ],
    GOING_TO_CLOSE: [
        "Vannu njann 🚶🐾",
        "Nice try. 😏"
    ],
    AFTER_CLOSING: [
        "Aah… ippo correct. ✨",
        "Problem solved. 😼",
        "You’re welcome. 💅"
    ],
    INSTAGRAM_OPENED: [
        "Ada Gommale",
        "Oru reel kude kanaam 🙂↕️ 🎬",
        "Ingane Ingane cheyy Baalu 💖"
    ],
    NETFLIX_OPENED: [
        "Now we’re talking netflix. 😎",
        "Just one episode. 🍿",
        "Work pinne cheyyaam. 💤"
    ],
    REOPENED_PRODUCTIVE: [
        "Ayyo… pinneyum? 💢",
        "Ithu ippo personal aanu. 🔥😾"
    ],
    SIGNATURE: [
        "Nee thurakku… njan adakkam.",
        "Poda kochu cherukka",
        "Same mistake, different app."
    ]
};

// Web Audio API Synthesizer (Meow & Paw Smash Sound FX)
let soundEnabled = true;
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playMeowSound() {
    if (!soundEnabled) return;
    try {
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(440, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.15);
        osc.frequency.exponentialRampToValueAtTime(600, audioCtx.currentTime + 0.3);
        
        gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.35);
        
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        
        osc.start();
        osc.stop(audioCtx.currentTime + 0.35);
    } catch (e) {
        console.log("Audio play error", e);
    }
}

function playSmashSound() {
    if (!soundEnabled) return;
    try {
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(150, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(30, audioCtx.currentTime + 0.2);
        
        gain.gain.setValueAtTime(0.5, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.25);
        
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        
        osc.start();
        osc.stop(audioCtx.currentTime + 0.25);
    } catch (e) {
        console.log("Audio play error", e);
    }
}

// Global Quote Player for Cards
window.playQuote = function(category) {
    if (DIALOGUES[category]) {
        const quotes = DIALOGUES[category];
        const quote = quotes[Math.floor(Math.random() * quotes.length)];
        showSimSpeech(quote, 4000);
        playMeowSound();
    }
};

// DOM Elements
const desktopScreen = document.getElementById("desktop-screen");
const simCat = document.getElementById("sim-cat");
const simCatImg = document.getElementById("sim-cat-img");
const simSpeech = document.getElementById("sim-speech");

const winVSCode = document.getElementById("win-vscode");
const winInsta = document.getElementById("win-insta");
const winNetflix = document.getElementById("win-netflix");

const btnVSCode = document.getElementById("btn-spawn-vscode");
const btnInsta = document.getElementById("btn-spawn-insta");
const btnNetflix = document.getElementById("btn-spawn-netflix");
const btnReset = document.getElementById("btn-reset-cat");
const btnSoundToggle = document.getElementById("btn-sound-toggle");

// Cat Simulator State
let catState = "IDLE"; // IDLE, IRRITATED, WALKING, SMASHING, HAPPY
let catPosX = 500;
let catPosY = 380;
let moveInterval = null;
let speechTimer = null;
let vscodeReopenCount = 0;
let walkStep = 0;

function setCatSprite(pose, facingLeft = false) {
    simCatImg.src = `sprites/cat_${pose}.png`;
    if (facingLeft) {
        simCatImg.style.transform = "scaleX(-1)";
    } else {
        simCatImg.style.transform = "scaleX(1)";
    }
}

function showSimSpeech(text, duration = 3000) {
    simSpeech.textContent = text;
    simSpeech.classList.remove("hidden");
    if (speechTimer) clearTimeout(speechTimer);
    speechTimer = setTimeout(() => {
        simSpeech.classList.add("hidden");
    }, duration);
}

function updateCatPosition(x, y) {
    catPosX = x;
    catPosY = y;
    simCat.style.left = `${x}px`;
    simCat.style.top = `${y}px`;
}

function resetCat() {
    if (moveInterval) clearInterval(moveInterval);
    catState = "IDLE";
    setCatSprite("idle");
    const rect = desktopScreen.getBoundingClientRect();
    updateCatPosition(rect.width - 150, rect.height - 130);
}

// Window Spawning & Cat Attack AI
btnVSCode.addEventListener("click", () => {
    winVSCode.classList.remove("hidden");
    playMeowSound();
    
    if (vscodeReopenCount > 0) {
        triggerCatAttack("REOPENED_PRODUCTIVE");
    } else {
        vscodeReopenCount++;
        triggerCatAttack("PRODUCTIVE_OPENED");
    }
});

btnInsta.addEventListener("click", () => {
    winInsta.classList.remove("hidden");
    triggerCatHappy("INSTAGRAM_OPENED");
});

btnNetflix.addEventListener("click", () => {
    winNetflix.classList.remove("hidden");
    triggerCatHappy("NETFLIX_OPENED");
});

btnReset.addEventListener("click", resetCat);

btnSoundToggle.addEventListener("click", () => {
    soundEnabled = !soundEnabled;
    btnSoundToggle.textContent = soundEnabled ? "🔊 Sound FX: ON" : "🔇 Sound FX: OFF";
});

// Close buttons inside simulated windows
document.getElementById("close-vscode").addEventListener("click", () => {
    winVSCode.classList.add("hidden");
});
document.getElementById("close-insta").addEventListener("click", () => {
    winInsta.classList.add("hidden");
});
document.getElementById("close-netflix").addEventListener("click", () => {
    winNetflix.classList.add("hidden");
});

function triggerCatAttack(category) {
    if (catState === "WALKING" || catState === "SMASHING") return;

    catState = "IRRITATED";
    setCatSprite("angry");
    
    const quotes = DIALOGUES[category];
    const quote = quotes[Math.floor(Math.random() * quotes.length)];
    showSimSpeech(quote, 2500);

    setTimeout(() => {
        startWalkToVSCode();
    }, 1000);
}

function startWalkToVSCode() {
    catState = "WALKING";
    walkStep = 0;
    
    const goingQuotes = DIALOGUES["GOING_TO_CLOSE"];
    showSimSpeech(goingQuotes[Math.floor(Math.random() * goingQuotes.length)], 3000);

    const closeBtn = document.getElementById("close-vscode");
    const closeRect = closeBtn.getBoundingClientRect();
    const screenRect = desktopScreen.getBoundingClientRect();

    // Target coordinates relative to desktop canvas
    const targetX = closeRect.left - screenRect.left - 40;
    const targetY = closeRect.top - screenRect.top - 20;

    if (moveInterval) clearInterval(moveInterval);

    moveInterval = setInterval(() => {
        const dx = targetX - catPosX;
        const dy = targetY - catPosY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const facingLeft = dx < 0;

        if (dist < 20) {
            clearInterval(moveInterval);
            executeSmash(facingLeft);
        } else {
            // Smooth small steps for visible leg movement
            const speed = Math.min(8, Math.max(3, dist / 10));
            updateCatPosition(catPosX + (dx / dist) * speed, catPosY + (dy / dist) * speed);
            
            // Alternate between walk1 and walk2 legs every 4 ticks
            walkStep++;
            const walkFrame = (Math.floor(walkStep / 4) % 2 === 0) ? "walk1" : "walk2";
            setCatSprite(walkFrame, facingLeft);
        }
    }, 30);
}

function executeSmash(facingLeft = false) {
    catState = "SMASHING";
    setCatSprite("smash", facingLeft);
    showSimSpeech("Bleh ;)", 1500);
    playSmashSound();

    setTimeout(() => {
        winVSCode.classList.add("hidden");
        setCatSprite("idle", facingLeft);
        
        const afterQuotes = DIALOGUES["AFTER_CLOSING"];
        showSimSpeech(afterQuotes[Math.floor(Math.random() * afterQuotes.length)], 3500);
        
        setTimeout(() => {
            catState = "IDLE";
        }, 3000);
    }, 450);
}

function triggerCatHappy(category) {
    if (catState === "WALKING" || catState === "SMASHING") return;
    catState = "HAPPY";
    setCatSprite("sit");
    playMeowSound();
    
    const quotes = DIALOGUES[category];
    showSimSpeech(quotes[Math.floor(Math.random() * quotes.length)], 3500);
    
    setTimeout(() => {
        catState = "IDLE";
        setCatSprite("idle");
    }, 4000);
}

// Make Simulated Windows Draggable
function makeDraggable(winEl) {
    const header = winEl.querySelector(".win-header");
    let isDragging = false;
    let offsetX, offsetY;

    header.addEventListener("mousedown", (e) => {
        isDragging = true;
        offsetX = e.clientX - winEl.offsetLeft;
        offsetY = e.clientY - winEl.offsetTop;
    });

    document.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        winEl.style.left = `${e.clientX - offsetX}px`;
        winEl.style.top = `${e.clientY - offsetY}px`;
    });

    document.addEventListener("mouseup", () => {
        isDragging = false;
    });
}

makeDraggable(winVSCode);
makeDraggable(winInsta);
makeDraggable(winNetflix);

// Update OS Clock
function updateClock() {
    const now = new Date();
    const clockEl = document.getElementById("os-clock");
    if (clockEl) {
        clockEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
}
setInterval(updateClock, 1000);
updateClock();

// Initial Setup
resetCat();