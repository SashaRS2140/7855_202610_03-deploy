import { mountGlowingCube } from './cube.js';

// --- CONFIGURATION ---
const PALETTE = [
    "#ffaa00", "#d65200", "#ff69b4",
    "#ff92f0", "#ff00ff", "#6f00d6",
    "#0000ff", "#60ffff", "#00ff00"
];

// --- STATE ---
let totalSeconds = 600;
let isRunning = false;
let cubeAPI = null;
let evtSource = null;
let currentColor = "#ffaa00"; // NEW: Track color for API saves
let hasUnsavedChanges = false;
// --- DOM ELEMENTS ---
const timerDisplay = document.getElementById('timer-display');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const cubeContainer = document.getElementById('cube-wrapper');
const colorMenu = document.getElementById('color-menu');
const colorTrigger = document.getElementById('color-trigger');

// NEW: Elements for Task Management
const taskSelect = document.getElementById("taskSelect");
const newTaskForm = document.getElementById("new-task-form");
const newTaskInput = document.getElementById("newTaskInput");
const saveNewTaskBtn = document.getElementById("saveNewTaskBtn");
const cancelNewTaskBtn = document.getElementById("cancelNewTaskBtn");
const saveTimerBtn = document.getElementById("saveTimerBtn");


// ======================================================
// 1. SERVER-SENT TIMER STREAM
// ======================================================

function connectTimerStream() {
    if (!timerDisplay) return;

    evtSource = new EventSource("/task/timer");

    evtSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);

            // Do not overwrite while user is editing OR has unsaved changes
            if (!timerDisplay.classList.contains('editing') && !hasUnsavedChanges) {
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


async function syncCurrentTask() {
    if (!taskSelect) return;

    try {
        const res = await fetch("/api/task/current");
        if (!res.ok) return;

        const data = await res.json();
        const current = data.current_task;

        if (!current) return;

        // Match option by value (task.id assumed to equal stored name)
        const option = [...taskSelect.options].find(
            opt => opt.value.toUpperCase() === current
        );

        if (option) {
            taskSelect.value = option.value;
        }
    } catch (err) {
        console.error("Failed to sync current task:", err);
    }
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

        // CLEAR the element safely and use a TextNode so we don't overwrite the input
        this.innerHTML = "";
        const textNode = document.createTextNode("00:00");
        this.appendChild(textNode);

        const input = document.createElement('input');
        input.type = 'tel'; // 'tel' forces the numeric keypad on mobile
        input.className = 'hidden-timer-input';
        input.setAttribute('autocomplete', 'off');

        // Stretch the hidden input over the timer so mobile taps register perfectly
        input.style.position = 'absolute';
        input.style.opacity = '0';
        input.style.height = '100%';
        input.style.width = '100%';
        input.style.top = '0';
        input.style.left = '0';

        this.appendChild(input);
        input.focus();

        const renderFromBuffer = () => {
            // If empty, reset to zeros
            if (!digitBuffer) {
                textNode.nodeValue = "00:00";
                return;
            }

            // Pad the string so we always have at least 4 digits for MM:SS
            const raw = digitBuffer.padStart(4, '0').padStart(6, '0');
            const h = raw.slice(-6, -4);
            const m = raw.slice(-4, -2);
            const s = raw.slice(-2);

            // Overflow to H:MM:SS only if there are hours
            if (parseInt(h, 10) > 0) {
                textNode.nodeValue = `${parseInt(h, 10)}:${m}:${s}`;
            } else {
                textNode.nodeValue = `${m}:${s}`;
            }
        };

        input.addEventListener('input', () => {
            // 1. Strip out anything that isn't a number
            let raw = input.value.replace(/\D/g, '');

            // 2. If it gets pushed past 6 digits, delete the most significant (leftmost) digit
            if (raw.length > 6) {
                raw = raw.slice(-6);
            }

            // 3. Keep the input and buffer in sync so mobile backspace works natively
            input.value = raw;
            digitBuffer = raw;

            renderFromBuffer();
        });

        const saveAndClose = () => {
            const raw = digitBuffer.padStart(6, '0');
            const h = parseInt(raw.slice(-6, -4), 10);
            const m = parseInt(raw.slice(-4, -2), 10);
            const s = parseInt(raw.slice(-2), 10);

            totalSeconds = (h * 3600) + (m * 60) + s;

            this.classList.remove('editing');
            this.innerHTML = textNode.nodeValue;


            hasUnsavedChanges = true;
            // Reveal the save button because the time was altered
            if (saveTimerBtn && taskSelect.value !== "new_task_trigger") {
                saveTimerBtn.classList.remove('hidden');

            }
        };

        // Leaving the field (blur) or pressing Enter will trigger saveAndClose
        input.addEventListener('blur', saveAndClose);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                input.blur(); // Blur forces it to run saveAndClose
            }
        });
    };
}


// ======================================================
// TASK MANAGEMENT (CREATE, SELECT, UPDATE)
// ======================================================
let previousTaskValue = taskSelect ? taskSelect.value : "";

if (taskSelect) {
    taskSelect.addEventListener("change", async (e) => {
        const selectedTask = e.target.value;
        hasUnsavedChanges = false;

        // 1. Toggle "Create New Task" UI
        if (selectedTask === "new_task_trigger") {
            taskSelect.classList.add("hidden");
            newTaskForm.classList.remove("hidden");
            newTaskInput.focus();
            return;
        }

        previousTaskValue = selectedTask;

        // 2. Set Current Task on Server
        try {
            await fetch("/task/current", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ task_name: selectedTask })
            });
            // Hide the save button if it was exposed from a previous task
            if (saveTimerBtn) saveTimerBtn.classList.add("hidden");
        } catch (err) {
            console.error("Failed to set current task:", err);
        }
    });
}

// 3. Cancel Creating a Task
if (cancelNewTaskBtn) {
    cancelNewTaskBtn.addEventListener("click", () => {
        newTaskForm.classList.add("hidden");
        taskSelect.classList.remove("hidden");
        taskSelect.value = previousTaskValue; // Revert to previously selected task
        newTaskInput.value = "";
    });
}

// 4. Save a BRAND NEW Task (POST)
if (saveNewTaskBtn) {
    saveNewTaskBtn.addEventListener("click", async (e) => {
        e.preventDefault(); // Prevents any accidental browser behaviors
        const taskName = newTaskInput.value.trim().toUpperCase();

        if (!taskName) return alert("Please enter a task name.");
        if (totalSeconds <= 0) return alert("Timer must be greater than 00:00.");

        try {
            // FIX: Added /api prefix
            const res = await fetch("/api/profile/preset", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    task_name: taskName,
                    task_time: totalSeconds,
                    task_color: currentColor
                })
            });

            // FIX: Safely check if the response is JSON before parsing
            const contentType = res.headers.get("content-type");
            let data = {};
            if (contentType && contentType.includes("application/json")) {
                data = await res.json();
            }

            if (res.ok) {
                hasUnsavedChanges = false;

                // Add to dropdown visually
                const newOption = document.createElement("option");
                newOption.value = taskName;
                newOption.textContent = taskName;
                taskSelect.insertBefore(newOption, taskSelect.lastElementChild);

                // Reset UI
                newTaskForm.classList.add("hidden");
                taskSelect.classList.remove("hidden");
                taskSelect.value = taskName;
                previousTaskValue = taskName;
                newTaskInput.value = "";

                // Visual Success Feedback
                timerDisplay.classList.add("flash-success");
                setTimeout(() => timerDisplay.classList.remove("flash-success"), 1000);

                // Set as active task
                await fetch("/api/task/current", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ task_name: taskName })
                });
            } else {
                alert(data.error || `Failed to create task (Status: ${res.status}).`);
            }
        } catch (err) {
            console.error("Error creating task:", err);
            alert("Network error: Could not reach the server.");
        }
    });
}

// 5. Update EXISTING Task Time (PUT)
if (saveTimerBtn) {
    saveTimerBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        const currentTask = taskSelect.value;
        if (!currentTask || currentTask === "new_task_trigger") return;

        try {
            // FIX: Added /api prefix
            const res = await fetch("/api/profile/preset", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    task_name: currentTask,
                    task_time: totalSeconds,
                    task_color: currentColor
                })
            });

            const contentType = res.headers.get("content-type");
            let data = {};
            if (contentType && contentType.includes("application/json")) {
                data = await res.json();
            }

            if (res.ok) {
                hasUnsavedChanges = false;

                // Hide button and flash success
                saveTimerBtn.classList.add("hidden");
                timerDisplay.classList.add("flash-success");
                setTimeout(() => timerDisplay.classList.remove("flash-success"), 1000);

                // Update the timer service backend
                await fetch("/api/task/current", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ task_name: currentTask })
                });
            } else {
                alert(data.error || `Failed to update task (Status: ${res.status}).`);
            }
        } catch (err) {
            console.error("Error updating task:", err);
            alert("Network error: Could not reach the server.");
        }
    });
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
            currentColor = color;
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
syncCurrentTask();