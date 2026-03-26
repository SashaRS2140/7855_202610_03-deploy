# Sprint 3 Report

- **Team Name:**  Team 3 : CUBE 
- **Sprint Dates:** 3-03-2026 → 26-03-2026  
- **Sprint Board Link:** [**[Trello](https://trello.com/invite/b/697954d1883f9190e1c7a774/ATTIfb7fe3865b854744cbb2eac186a07e0aE569C07D/7855202610-3)**]  
- **GitHub Repository Link:** [[**Github**](https://github.com/BrycesDevices/7855_202610_03.git)]

## 1. Sprint Board Screenshots
*Provide screenshots of your Sprint 3 board filtered by each team member.*
- **[Member 1]:** `images/sprint3-board-[member1].png`
- **[Member 2]:** `images/sprint3-board-[member2].png`

## 2. Sprint Review (Planned vs. Delivered)
*Review what you planned to accomplish this sprint versus what was actually completed. Focus on your architecture, testing, and UI goals.*

**Successfully Delivered:**

### Back-End Goals:
-	Remodularization 
-	Finish updating security

-	Testing 
-	Added post-hoc -  Session Storage to repository. 

Cube registration and pattern creation were cute for sprint feasibility
#### Front-End Goals:
-	Bug fixes
-	Error Handling 
-	CSR vs SSR – Explain
-	Check RGBW Hex 
#### Hardware Goals:
-	Connect to back end 

**Not Completed / Partially Completed:**

#### Back-End
-	Add pattern and color management to API routes - 
-	Cube registration
#### Front-End
-   Cube registration

-	Manage Cube-IDs – Network Connection
-	Pattern management via API

We pushed the manage cube-IDs and pattern management back because the scope of work was too large to implement along side proper testing and refactorization. 

## 3. Architecture & UI Strategy
**Code Modularization:**  
**TO BE UPDATED TO CORRECT**
``` src/
    ├── server/
    │   ├── routes/
    │   │   ├── auth_routes.py        # login, signup, logout
    │   │   ├── web_routes.py         # dashboard, profile UI
    │   │   └── api_routes.py         # user API & ESP32 telemetry
    │   ├── services/
    │   │   ├── session_services.py   # Core business logic
    │   │   ├── timer_service.py      # CountupTimer logic
    │   │   └── validation.py         # Extracted input validation helpers
    │   ├── repository.py             # Firestore Data Access Layer
    │   └── decorators/
    │       └── auth.py               # @login_required, @require_api_key
    ├── static/
    │   ├── css/style.css
    │   └── js/                       # CSR logic
    │       ├── cube.js               # Three.js logic
    │       └── dashboard.js          # DOM manipulation & fetching
    └── templates/                    # Jinja2 HTML templates
```
[Briefly describe your folder structure. How did you break apart your `app.py`?]


**SSR and CSR Breakdown**

We employ a hybrid rendering approach to optimize both initial load times and real-time interactivity.

- **Server-Side Rendering (SSR):** Flask and Jinja2 template engine are responsible for rendering the initial state of the application. This includes base layouts (base.html), authentication pages (login.html, signup.html), and the initial load of the Dashboard. For instance, the server populates the initial user task dropdown ({% for task in tasks %}) and injects secure environment variables (like the Firebase Web API key) directly into the initial HTML payload.

- **Client-Side Rendering (CSR) & DOM Manipulation:** Highly interactive components are deferred to the client.

    - **3D Graphics:** The cube.js module utilizes Three.js to render and animate the interactive glowing cube entirely on the client's GPU.

    - **Real-time UI Updates:** dashboard.js heavily relies on CSR to manage state without page reloads. It handles asynchronous form submissions (creating/updating tasks via fetch), dynamic UI toggling (switching between task selection and the "new task" form), and ATM-style input masking for the timer.

    - **Server-Sent Events (SSE):** The timer display is updated purely via client-side DOM manipulation, listening to a continuous stream from the server (new EventSource("/task/timer")) to reflect countdowns and overtime in real-time.

## 4. Automated Testing & Coverage
- **Testing Framework:** `pytest`
- **Current Code Coverage:** [75%]
- **Mocked Components:** 
    - Firestore
    - ** Go Through Later**

**Test Highlight:**
```python
# Paste ONE test here that demonstrates the AAA pattern and Mocking/Parametrization