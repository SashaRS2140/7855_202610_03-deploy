import { mountGlowingCube } from './cube.js';

// --- CONFIGURATION ---
const PALETTE = [
    "#ffaa00", "#d65200", "#ff69b4",
    "#ff92f0", "#ff00ff", "#6f00d6",
    "#0000ff", "#60ffff", "#00ff00"
];

// --- STATE ---
let totalSeconds = 600; // Used only for editing buffer
let isRunning = false;
let cubeAPI = null; // Will hold the 3D controls
let evtSource = null;

// --- DOM ELEMENTS ---
const timerDisplay = document.getElementById('timer-display');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const cubeContainer = document.getElementById('cube-wrapper');
const colorMenu = document.getElementById('color-menu');
const colorTrigger = document.getElementById('color-trigger');


// ======================================================
// 1. SERVER-SENT TIMER STREAM
// ======================================================

function connectTimerStream() {
    if (!timerDisplay) return;

    evtSource = new EventSource("/task/timer");

    evtSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);

            // Do not overwrite while user is editing
            if (!timerDisplay.classList.contains('editing')) {
                timerDisplay.innerText = data.display_mmss;
            }

            // Optional visual overtime indicator
            if (data.mode === "overtime") {
                timerDisplay.classList.add("overtime");
            } else {
                timerDisplay.classList.remove("overtime");
            }

        } catch (err) {
            console.error("Failed to parse timer stream:", err);
        }
    };

    evtSource.onerror = (err) => {
        console.error("Timer stream connection error:", err);
    };
}


// ======================================================
// 2. EDIT INPUT (ATM / MICROWAVE STYLE)
// ======================================================

if (timerDisplay) {
    timerDisplay.style.cursor = "pointer";
    timerDisplay.style.position = "relative";

    timerDisplay.onclick = function() {
        if (this.classList.contains('editing')) return;

        this.classList.add('editing');

        let digitBuffer = "";
        this.innerText = "00:00";

        const input = document.createElement('input');
        input.type = 'tel';
        input.className = 'hidden-timer-input';
        input.setAttribute('autocomplete', 'off');
        this.appendChild(input);
        input.focus();

        const renderFromBuffer = () => {
            const raw = digitBuffer.padStart(6, '0');
            const h = raw.slice(0, 2);
            const m = raw.slice(2, 4);
            const s = raw.slice(4, 6);

            if (parseInt(h) > 0) {
                this.innerText = `${parseInt(h)}:${m}:${s}`;
            } else {
                this.innerText = `${m}:${s}`;
            }
        };

        input.addEventListener('input', (e) => {
            const val = e.data;
            const inputType = e.inputType;

            if (inputType === 'deleteContentBackward') {
                digitBuffer = digitBuffer.slice(0, -1);
            } else if (val && /^[0-9]$/.test(val)) {
                if (digitBuffer.length < 6) {
                    digitBuffer += val;
                }
            }

            input.value = "";
            renderFromBuffer();
        });

        const saveAndClose = () => {
            const raw = digitBuffer.padStart(6, '0');
            const h = parseInt(raw.slice(0, 2));
            const m = parseInt(raw.slice(2, 4));
            const s = parseInt(raw.slice(4, 6));
            totalSeconds = (h * 3600) + (m * 60) + s;

            this.classList.remove('editing');
            if (this.contains(input)) {
                this.removeChild(input);
            }

            // NOTE: At this point you would POST totalSeconds to your backend
            // so the server timer target updates.
            // Example:
            // fetch("/task/control", {
            //   method: "POST",
            //   headers: {"Content-Type": "application/json"},
            //   body: JSON.stringify({ action: "reset", seconds: totalSeconds })
            // });
        };

        input.addEventListener('blur', saveAndClose);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') input.blur();
        });
    };
}


// ======================================================
// 3. PLAYBACK CONTROLS (SERVER-DRIVEN TIMER)
// ======================================================

if (startBtn) {
    startBtn.addEventListener('click', () => {
        if (isRunning) return;
        isRunning = true;

        if (cubeAPI) cubeAPI.setBreathing(true);

        // Tell server to start timer
        fetch("/task/control", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ action: "start" })
        }).catch(console.error);
    });
}

if (stopBtn) {
    stopBtn.addEventListener('click', () => {
        isRunning = false;
        if (cubeAPI) cubeAPI.setBreathing(false);

        fetch("/task/control", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ action: "stop" })
        }).catch(console.error);
    });
}


// ======================================================
// 4. COLOR PICKER & CUBE INIT
// ======================================================

// Initialize Cube
if (cubeContainer) {
    cubeAPI = mountGlowingCube(cubeContainer);
}

// Initialize Color Picker
if (colorMenu && colorTrigger) {
    PALETTE.forEach(color => {
        const btn = document.createElement('button');
        btn.className = 'swatch';
        btn.style.backgroundColor = color;

        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (cubeAPI) cubeAPI.setColor(color);
            colorTrigger.style.backgroundColor = color;
            colorMenu.classList.remove('active');
        });
        colorMenu.appendChild(btn);
    });

    colorTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        colorMenu.classList.toggle('active');
    });

    document.addEventListener('click', (e) => {
        if (!colorMenu.contains(e.target) && e.target !== colorTrigger) {
            colorMenu.classList.remove('active');
        }
    });
}


// ======================================================
// INIT
// ======================================================

connectTimerStream();