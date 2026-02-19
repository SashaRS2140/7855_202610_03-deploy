import { mountGlowingCube } from './cube.js';

// --- CONFIGURATION ---
const PALETTE = [
    "#ffaa00", "#d65200", "#ff69b4",
    "#ff92f0", "#ff00ff", "#6f00d6",
    "#0000ff", "#60ffff", "#00ff00"
];

// --- STATE ---
let totalSeconds = 600; // Default 10:00
let timerInterval = null;
let isRunning = false;
let cubeAPI = null; // Will hold the 3D controls

// --- DOM ELEMENTS ---
const timerDisplay = document.getElementById('timer-display');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const cubeContainer = document.getElementById('cube-wrapper');
const colorMenu = document.getElementById('color-menu');
const colorTrigger = document.getElementById('color-trigger');


// ======================================================
// 1. TIMER LOGIC
// ======================================================

function formatTime(sec) {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = sec % 60;
    const pad = (n) => n.toString().padStart(2, '0');
    return h > 0 ? `${h}:${pad(m)}:${pad(s)}` : `${pad(m)}:${pad(s)}`;
}

function updateDisplay() {
    // Only update if we are NOT currently editing
    if (timerDisplay && !timerDisplay.classList.contains('editing')) {
        timerDisplay.innerText = formatTime(totalSeconds);
    }
}

function stopTimer() {
    isRunning = false;
    clearInterval(timerInterval);
    if (cubeAPI) cubeAPI.setBreathing(false);
}

window.adjustTime = function(amount) {
    totalSeconds += amount;
    if (totalSeconds < 0) totalSeconds = 0;
    updateDisplay();
};

// --- ATM / MICROWAVE STYLE INPUT LOGIC ---
if (timerDisplay) {
    timerDisplay.style.cursor = "pointer";
    timerDisplay.style.position = "relative";

    timerDisplay.onclick = function() {
        // 1. Prevent double-initialization
        if (this.classList.contains('editing')) return;

        // 2. Stop Timer and Enter Edit Mode
        stopTimer();
        this.classList.add('editing');

        // 3. Initialize Digit Buffer
        let digitBuffer = "";
        this.innerText = "00:00"; // Initial view

        // 4. Create Invisible Input (Captures Mobile Keyboard)
        const input = document.createElement('input');
        input.type = 'tel'; // Triggers numeric keypad on mobile
        input.className = 'hidden-timer-input';
        input.setAttribute('autocomplete', 'off');
        this.appendChild(input);
        input.focus();

        // 5. Helper: Format Buffer into Time (The Shifting Logic)
        const renderFromBuffer = () => {
            // Pad string to ensure we have enough digits (e.g. "1" -> "000001")
            const raw = digitBuffer.padStart(6, '0');

            // Slice out HMS
            const h = raw.slice(0, 2);
            const m = raw.slice(2, 4);
            const s = raw.slice(4, 6);

            // Display logic
            if (parseInt(h) > 0) {
                this.innerText = `${parseInt(h)}:${m}:${s}`; // 1:05:00
            } else {
                this.innerText = `${m}:${s}`; // 05:00
            }
        };

        // 6. Handle Input (Typing)
        input.addEventListener('input', (e) => {
            const val = e.data;
            const inputType = e.inputType; // Detect backspace vs text

            // Handle Backspace (deleteContentBackward)
            if (inputType === 'deleteContentBackward') {
                digitBuffer = digitBuffer.slice(0, -1);
            }
            // Handle Number Entry
            else if (val && /^[0-9]$/.test(val)) {
                // Max 6 digits (99 hours, 99 mins, 99 secs)
                if (digitBuffer.length < 6) {
                    digitBuffer += val;
                }
            }

            // Update visual text without cursor
            // We strip the actual input value so the browser doesn't scroll/shift
            input.value = "";
            renderFromBuffer();
        });

        // 7. Save & Exit Function
        const saveAndClose = () => {
            // Calculate Seconds from Buffer
            const raw = digitBuffer.padStart(6, '0');
            const h = parseInt(raw.slice(0, 2));
            const m = parseInt(raw.slice(2, 4));
            const s = parseInt(raw.slice(4, 6));

            const newTotal = (h * 3600) + (m * 60) + s;

            // Only update if user actually typed something, otherwise revert
            if (digitBuffer.length > 0) {
                totalSeconds = newTotal;
            }

            // Cleanup DOM
            this.classList.remove('editing');
            if(this.contains(input)) {
                this.removeChild(input);
            }
            updateDisplay(); // Re-render standard view
        };

        // 8. Exit Triggers
        input.addEventListener('blur', saveAndClose); // Click away
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                input.blur(); // Triggers saveAndClose
            }
        });
    };
}

// ======================================================
// 2. PLAYBACK CONTROLS
// ======================================================

if (startBtn) {
    startBtn.addEventListener('click', () => {
        if (isRunning) return;
        isRunning = true;

        // Start Cube Breathing
        if (cubeAPI) cubeAPI.setBreathing(true);

        timerInterval = setInterval(() => {
            if (totalSeconds > 0) {
                totalSeconds--;
                updateDisplay();
            } else {
                stopTimer();
            }
        }, 1000);
    });
}

if (stopBtn) {
    stopBtn.addEventListener('click', stopTimer);
}


// ======================================================
// 3. COLOR PICKER & CUBE INIT
// ======================================================

// Initialize Cube
if (cubeContainer) {
    cubeAPI = mountGlowingCube(cubeContainer);
}

// Initialize Color Picker
if (colorMenu && colorTrigger) {
    // 1. Generate Swatches
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

    // 2. Toggle Menu
    colorTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        colorMenu.classList.toggle('active');
    });

    // 3. Close on Outside Click
    document.addEventListener('click', (e) => {
        if (!colorMenu.contains(e.target) && e.target !== colorTrigger) {
            colorMenu.classList.remove('active');
        }
    });
}

// Initial Render
updateDisplay();