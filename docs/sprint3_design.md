# Architecture & UI Specification

## 1. Modularization Strategy

**Current Architecture:** Our application currently follows a multi-tiered Service-Oriented Architecture using Flask. It separates concerns into Controllers (web_controller.py, api_controller.py), Services (session_services.py, timer_sevice.py), and a Data Access Layer (repository.py using Firestore). While this provides a basic separation between routing, business logic, and database operations, our current controllers and service files are becoming bloated, mixing authentication, validation, and routing.

**Rooms for Improvement & Future Plans:**
To enforce a stricter separation of concerns and improve scalability, we are refactoring our architecture to map exactly to our domain needs. We are abandoning generic boilerplate (like nested __init__.py files) in favor of a clean, flat, feature-driven structure within our src directory. Cross-cutting concerns like validation and authentication decorators will be extracted from the bloated service files into dedicated utility modules.

### Our target structure for this sprint is as follows:
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

## 2. SSR and CSR Breakdown

We employ a hybrid rendering approach to optimize both initial load times and real-time interactivity.

- **Server-Side Rendering (SSR):** Flask and Jinja2 template engine are responsible for rendering the initial state of the application. This includes base layouts (base.html), authentication pages (login.html, signup.html), and the initial load of the Dashboard. For instance, the server populates the initial user task dropdown ({% for task in tasks %}) and injects secure environment variables (like the Firebase Web API key) directly into the initial HTML payload.

- **Client-Side Rendering (CSR) & DOM Manipulation:** Highly interactive components are deferred to the client.

    - **3D Graphics:** The cube.js module utilizes Three.js to render and animate the interactive glowing cube entirely on the client's GPU.

    - **Real-time UI Updates:** dashboard.js heavily relies on CSR to manage state without page reloads. It handles asynchronous form submissions (creating/updating tasks via fetch), dynamic UI toggling (switching between task selection and the "new task" form), and ATM-style input masking for the timer.

    - **Server-Sent Events (SSE):** The timer display is updated purely via client-side DOM manipulation, listening to a continuous stream from the server (new EventSource("/task/timer")) to reflect countdowns and overtime in real-time.

## 3. Security Measures

Our security posture relies on strict authentication protocols, robust input sanitization, and database query limits.

- **Authentication & Authorization:** *Web Clients:* We use Firebase Authentication. The client authenticates directly with Firebase, receives a JWT, and passes it to our Flask backend. We use a @login_required decorator that verifies the cryptographic signature of the JWT via the Firebase Admin SDK (auth.verify_id_token) before granting route access.

    - **Hardware (ESP32):** Hardware endpoints use a static key verification approach (@require_api_key). Because this key is embedded in the hardware and effectively public, we strictly limit its capabilities:

    - **Route Isolation:** The @require_api_key is exclusively applied to hardware-specific endpoints (e.g., /task/control, /esp/telemetry). It provides absolutely zero access to user profile endpoints, preset configurations, or auth routes.

    - **Strict Action Scoping:** On the allowed routes, the payload is restricted to specific hardware actions (e.g., start, stop, reset). It cannot perform open-ended database writes.

    - **Hardware-to-User Binding:** Even with the public API key, operations require a registered cube_uuid. The server verifies that the UUID is actively paired to a specific user account (uid = sess_svc.get_cube_user(cube_uuid)) before taking action, ensuring the hardware can only interact with its designated, sandboxed session state.

- **Strict Input Validation:** To prevent injection attacks and data corruption, all incoming JSON payloads and form data run through strict validation functions (moving to utils/validation.py). This includes:

    - **Whitelist Checking:** Rejecting requests that contain unknown or unexpected payload fields.

    - **Type & Bounds Checking:** Enforcing length limits (e.g., maximum 50 characters for strings, 99-minute limits on timers) and strictly enforcing integer types.

    - **Regex Pattern Matching:** Enforcing specific formats, such as restricting colors to valid hex RGB strings (^#[0-9a-fA-F]{6}$) and enforcing alphanumeric password rules.

- **Database Isolation & Content-Type Enforcement:** Firestore queries are strictly isolated by the verified uid extracted from the JWT, ensuring users can never query or modify another user's documents. Additionally, all API endpoints are guarded by a require_json_content_type() check to prevent CSRF vulnerabilities associated with simple form POSTs.