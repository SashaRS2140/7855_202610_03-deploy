const timerDisplay = document.getElementById("timer-display");
    const startBtn = document.getElementById("startBtn");
    const stopBtn = document.getElementById("stopBtn");

    // Default time in seconds (11:11 = 671 seconds)
    let currentSeconds = 671;
    let isRunning = false;
    let eventSource = null;

    // Helper: Format Seconds to MM:SS
    function updateDisplay(totalSeconds) {
        const m = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
        const s = (totalSeconds % 60).toString().padStart(2, '0');
        timerDisplay.textContent = `${m}:${s}`;
    }

    // 1. Arrow Button Logic (Update Set Time)
    // Only works if timer is NOT running
    window.adjustTime = function(amount) {
        if(isRunning) return; // Lock controls while running

        currentSeconds += amount;
        if(currentSeconds < 0) currentSeconds = 0;
        updateDisplay(currentSeconds);
    };

    // 2. Play Button Logic
    startBtn.addEventListener("click", function() {
        if(isRunning) return;
        isRunning = true;

        // TODO: In the future, POST to API to set start time
        // For now, we connect to your existing stream
        connectToTimerStream();
    });

    // 3. Stop Button Logic
    stopBtn.addEventListener("click", function() {
        isRunning = false;
        if(eventSource) {
            eventSource.close();
            eventSource = null;
        }
        // Creates a visual stop effect
        timerDisplay.style.opacity = "0.5";
        setTimeout(() => timerDisplay.style.opacity = "1", 200);
    });

    // 4. SSE Connection (Your existing logic, wrapped)
    function connectToTimerStream() {
        if(eventSource) eventSource.close();

        eventSource = new EventSource("/task/timer");

        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            timerDisplay.textContent = data.remaining_mmss;

            // Optional: Update local seconds to match server
            currentSeconds = data.remaining_seconds;
        };
    }

    // Initialize display
    updateDisplay(currentSeconds);