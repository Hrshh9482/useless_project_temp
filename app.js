// Kuttan the Desktop Poocha — Interactive Web Simulator & Audio Engine

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
        "You're welcome. 💅"
    ],
    INSTAGRAM_OPENED: [
        "Ada Gommale",
        "Oru reel kude kanaam 🙂↕️ 🎬",
        "Ingane Ingane cheyy Baalu 💖"
    ],
    NETFLIX_OPENED: [
        "Now we're talking netflix. 😎",
        "Just one episode. 🍿",
        "Work pinne cheyyaam. 💤"
    ],
    REOPENED_PRODUCTIVE: [
        "Ayyo… pinneyum? 💢",
        "Ithu ippo personal aanu. 🔥😾"
    ],
    GIGGLE: [
        "Hehehe… tickles! 😸✨",
        "Kili kili! 😸",
        "happy happy happyy 😸💖",
        "Enthaappa ithu? 😸"
    ],
    SLEEP: [
        "Zzz... 💤",
        "Sshh... njan uranguva 😴",
        "Night night 💤"
    ]
};

// Audio
let soundEnabled = true;
let audioCtx = null;
let meowAudio = null;

function getAudioCtx() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    return audioCtx;
}

function initMeowAudio() {
    if (!meowAudio) {
        meowAudio = new Audio('sound/meow.mp3');
        meowAudio.volume = 0.7;
    }
}

function playMeowSound() {
    if (!soundEnabled) return;
    initMeowAudio();
    try {
        const clone = meowAudio.cloneNode();
        clone.volume = 0.7;
        clone.play().catch(() => {
            const ctx = getAudioCtx();
            if (ctx.state === 'suspended') ctx.resume();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(440, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15);
            osc.frequency.exponentialRampToValueAtTime(600, ctx.currentTime + 0.3);
            gain.gain.setValueAtTime(0.3, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.35);
        });
    } catch (e) { console.log('Meow error:', e); }
}

function playSmashSound() {
    if (!soundEnabled) return;
    try {
        const ctx = getAudioCtx();
        if (ctx.state === 'suspended') ctx.resume();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(150, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(30, ctx.currentTime + 0.2);
        gain.gain.setValueAtTime(0.5, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.25);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.25);
    } catch (e) { console.log('Smash error:', e); }
}

// Quote player for dialogue cards
window.playQuote = function(category) {
    if (DIALOGUES[category]) {
        const quotes = DIALOGUES[category];
        const quote = quotes[Math.floor(Math.random() * quotes.length)];
        showSimSpeech(quote, 4000);
        playMeowSound();
    }
};

// DOM
const desktopScreen = document.getElementById('desktop-screen');
const simCat = document.getElementById('sim-cat');
const simCatImg = document.getElementById('sim-cat-img');
const simSpeech = document.getElementById('sim-speech');

const winVSCode = document.getElementById('win-vscode');
const winLeetCode = document.getElementById('win-leetcode');
const winInsta = document.getElementById('win-insta');
const winNetflix = document.getElementById('win-netflix');

const btnVSCode = document.getElementById('btn-spawn-vscode');
const btnLeetCode = document.getElementById('btn-spawn-leetcode');
const btnInsta = document.getElementById('btn-spawn-insta');
const btnNetflix = document.getElementById('btn-spawn-netflix');
const btnReset = document.getElementById('btn-reset-cat');
const btnSoundToggle = document.getElementById('btn-sound-toggle');

// Cat state
let catState = 'IDLE';
let catPosX = 500;
let catPosY = 350;
let moveInterval = null;
let speechTimer = null;
let idleSleepTimer = null;
let productiveOpenCount = 0;
let walkStep = 0;
let targetWin = null;

function setCatSprite(pose, facingLeft = false) {
    simCatImg.src = `sprites/cat_${pose}.png`;
    simCatImg.style.transform = facingLeft ? 'scaleX(-1)' : 'scaleX(1)';
}

function showSimSpeech(text, duration = 3000) {
    simSpeech.textContent = text;
    simSpeech.classList.remove('hidden');
    if (speechTimer) clearTimeout(speechTimer);
    speechTimer = setTimeout(() => {
        simSpeech.classList.add('hidden');
    }, duration);
}

function updateCatPosition(x, y) {
    catPosX = x;
    catPosY = y;
    simCat.style.left = `${x}px`;
    simCat.style.top = `${y}px`;
}

function startIdleSleepTimer() {
    if (idleSleepTimer) clearTimeout(idleSleepTimer);
    idleSleepTimer = setTimeout(() => {
        if (catState === 'IDLE') {
            catState = 'SLEEPING';
            setCatSprite('sleep');
            const q = DIALOGUES.SLEEP;
            showSimSpeech(q[Math.floor(Math.random() * q.length)], 4000);
        }
    }, 3000);
}

function resetCat() {
    if (moveInterval) { clearInterval(moveInterval); moveInterval = null; }
    catState = 'IDLE';
    setCatSprite('idle');
    if (desktopScreen) {
        const rect = desktopScreen.getBoundingClientRect();
        updateCatPosition(rect.width - 150, rect.height - 130);
    }
    startIdleSleepTimer();
}

// Click cat = giggle
if (simCat) {
    simCat.addEventListener('click', () => {
        if (catState === 'IDLE' || catState === 'SLEEPING' || catState === 'HAPPY') {
            catState = 'GIGGLING';
            setCatSprite('giggle');
            playMeowSound();
            const q = DIALOGUES.GIGGLE;
            showSimSpeech(q[Math.floor(Math.random() * q.length)], 2000);
            setTimeout(() => {
                catState = 'IDLE';
                setCatSprite('idle');
                startIdleSleepTimer();
            }, 2000);
        }
    });
}

// Productive windows trigger attack
function openProductiveWindow(winEl, closeId) {
    winEl.classList.remove('hidden');
    playMeowSound();
    productiveOpenCount++;
    targetWin = { el: winEl, closeId };
    if (productiveOpenCount > 1) {
        triggerCatAttack('REOPENED_PRODUCTIVE');
    } else {
        triggerCatAttack('PRODUCTIVE_OPENED');
    }
}

if (btnVSCode) btnVSCode.addEventListener('click', () => openProductiveWindow(winVSCode, 'close-vscode'));
if (btnLeetCode) btnLeetCode.addEventListener('click', () => openProductiveWindow(winLeetCode, 'close-leetcode'));

// Distraction windows = cat happy
if (btnInsta) btnInsta.addEventListener('click', () => {
    winInsta.classList.remove('hidden');
    triggerCatHappy('INSTAGRAM_OPENED');
});

if (btnNetflix) btnNetflix.addEventListener('click', () => {
    winNetflix.classList.remove('hidden');
    triggerCatHappy('NETFLIX_OPENED');
});

if (btnReset) btnReset.addEventListener('click', () => {
    // Hide all windows
    [winVSCode, winLeetCode, winInsta, winNetflix].forEach(w => {
        if (w) w.classList.add('hidden');
    });
    productiveOpenCount = 0;
    resetCat();
});

if (btnSoundToggle) {
    btnSoundToggle.addEventListener('click', () => {
        soundEnabled = !soundEnabled;
        btnSoundToggle.textContent = soundEnabled ? '🔊 Sound ON' : '🔇 Sound OFF';
    });
}

// Close buttons
['close-vscode', 'close-leetcode', 'close-insta', 'close-netflix'].forEach(id => {
    const btn = document.getElementById(id);
    if (btn) {
        btn.addEventListener('click', () => {
            btn.closest('.sim-window').classList.add('hidden');
        });
    }
});

function triggerCatAttack(category) {
    if (catState === 'WALKING' || catState === 'SMASHING') return;
    catState = 'IRRITATED';
    setCatSprite('angry');
    const q = DIALOGUES[category];
    showSimSpeech(q[Math.floor(Math.random() * q.length)], 2500);
    setTimeout(() => startWalkToTarget(), 1000);
}

function startWalkToTarget() {
    if (!targetWin) return;
    catState = 'WALKING';
    walkStep = 0;
    const goQ = DIALOGUES.GOING_TO_CLOSE;
    showSimSpeech(goQ[Math.floor(Math.random() * goQ.length)], 3000);

    const closeBtn = document.getElementById(targetWin.closeId);
    if (!closeBtn || !desktopScreen) return;
    const closeRect = closeBtn.getBoundingClientRect();
    const screenRect = desktopScreen.getBoundingClientRect();
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
            moveInterval = null;
            executeSmash(facingLeft);
        } else {
            const speed = Math.min(8, Math.max(3, dist / 10));
            updateCatPosition(catPosX + (dx / dist) * speed, catPosY + (dy / dist) * speed);
            walkStep++;
            const frame = (Math.floor(walkStep / 4) % 2 === 0) ? 'walk1' : 'walk2';
            setCatSprite(frame, facingLeft);
        }
    }, 30);
}

function executeSmash(facingLeft = false) {
    catState = 'SMASHING';
    setCatSprite('smash', facingLeft);
    showSimSpeech('Bleh ;)', 1500);
    playSmashSound();

    setTimeout(() => {
        if (targetWin && targetWin.el) {
            targetWin.el.classList.add('hidden');
        }
        targetWin = null;
        setCatSprite('idle', facingLeft);
        const aq = DIALOGUES.AFTER_CLOSING;
        showSimSpeech(aq[Math.floor(Math.random() * aq.length)], 3500);
        setTimeout(() => {
            catState = 'IDLE';
            startIdleSleepTimer();
        }, 3000);
    }, 450);
}

function triggerCatHappy(category) {
    if (catState === 'WALKING' || catState === 'SMASHING') return;
    catState = 'HAPPY';
    setCatSprite('sit');
    playMeowSound();
    const q = DIALOGUES[category];
    showSimSpeech(q[Math.floor(Math.random() * q.length)], 3500);
    setTimeout(() => {
        catState = 'IDLE';
        setCatSprite('idle');
        startIdleSleepTimer();
    }, 4000);
}

// Make windows draggable
function makeDraggable(winEl) {
    if (!winEl) return;
    const header = winEl.querySelector('.win-header');
    if (!header) return;
    let isDragging = false;
    let offsetX, offsetY;

    header.addEventListener('mousedown', (e) => {
        isDragging = true;
        const parentRect = winEl.parentElement.getBoundingClientRect();
        offsetX = e.clientX - winEl.offsetLeft;
        offsetY = e.clientY - winEl.offsetTop;
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        winEl.style.left = `${e.clientX - offsetX}px`;
        winEl.style.top = `${e.clientY - offsetY}px`;
    });

    document.addEventListener('mouseup', () => { isDragging = false; });
}

[winVSCode, winLeetCode, winInsta, winNetflix].forEach(w => makeDraggable(w));

// Clock
function updateClock() {
    const now = new Date();
    const el = document.getElementById('os-clock');
    if (el) el.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
setInterval(updateClock, 1000);
updateClock();

// Smooth scroll for nav
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
        const target = document.querySelector(a.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Init
resetCat();
