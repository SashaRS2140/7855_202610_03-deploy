# Sprint 3 Report

- **Team Name:** [Team Name Here]  
- **Sprint Dates:** [Start → End]  
- **Sprint Board Link:** [Link]  
- **GitHub Repository Link:** [Link]

## 1. Sprint Board Screenshots
*Provide screenshots of your Sprint 3 board filtered by each team member.*
- **[Member 1]:** `images/sprint3-board-[member1].png`
- **[Member 2]:** `images/sprint3-board-[member2].png`

## 2. Sprint Review (Planned vs. Delivered)
*Review what you planned to accomplish this sprint versus what was actually completed. Focus on your architecture, testing, and UI goals.*

**Successfully Delivered:**
- [Feature/Task 1]: [Brief description of the implementation, e.g., "Modularized the database logic into a `services` folder."]
- [Feature/Task 2]: [e.g., "Mocked Firestore and achieved 80% coverage on the profile endpoint."]
- [Feature/Task 3]: [e.g., "Integrated Chart.js on the frontend using CSR."]

**Not Completed / Partially Completed:**
*Explain why these were not finished. (e.g., Underestimated complexity, spent more time writing quality tests for a single endpoint rather than rushing multiple endpoints, blockers with Mocking, etc.)*
- [Feature/Task 1]: [Reason]
- [Feature/Task 2]: [Reason]

## 3. Architecture & UI Strategy
**Code Modularization:**  
[Briefly describe your folder structure. How did you break apart your `app.py`?]

**SSR + CSR Breakdown:**  
- **Server-Side (Flask):** [What does Flask render? e.g., Base templates, initial layout]
- **Client-Side (JS):** [What does JS handle? e.g., Fetching sensor data, updating Chart.js]

## 4. Automated Testing & Coverage
- **Testing Framework:** `pytest`
- **Current Code Coverage:** [%]
- **Mocked Components:** [List what was mocked, e.g., `verify_id_token`, Firestore]

**Test Highlight:**
```python
# Paste ONE test here that demonstrates the AAA pattern and Mocking/Parametrization