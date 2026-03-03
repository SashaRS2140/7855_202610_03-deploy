# Sprint 2 Report



---

## 1. Sprint Overview

- **Your Team Name:** [**Team 2**]  
- **Sprint 2 Dates:** [**10/02/2026 → 03/03/2026**]  
- **Sprint Goal:** 
    *Implement feature dashboard connection for timer implementation with **Firestore persistence** and **safe validation**. data should be personal to each user and users should be able to login via email.*

---

## 2. Sprint Board

**Sprint Board Link:** [**[Trello](https://trello.com/invite/b/697954d1883f9190e1c7a774/ATTIfb7fe3865b854744cbb2eac186a07e0aE569C07D/7855202610-3)**]  
**GitHub Repository Link:** [[**Github**](https://github.com/BrycesDevices/7855_202610_03.git)]

---

### 2.1 Sprint Board Screenshot (Filtered by Team Member)

**Please provide a screenshot of your Sprint 2 board** (e.g., Trello, GitHub Projects) **filtered by each team member**. This makes the review concrete and shows shared ownership.

- **[Sasha Roosen-Saba] Board Screenshot:**  
  ![alt text](image.png)

- **[Bryce Reid] Board Screenshot:**  
  ![alt text](image-1.png)

- **[Perry Zhou] Board Screenshot:**  
  ![alt text](image-2.png)
- **[Kale Wyse] Board Screenshot:**  
![image-4.png](image-4.png)

---

### 2.2 Completed vs. Not Completed (Feature-Focused)

**Plan** 
SPRINT 2:

- **Web UI framework placeholders**
- **communication protocol between server + cube**
(or mock cube client)
- **Database framework** - Ability to store necessary data on firebase securely
- **Cube-Client control** to start, stop session, & reset session.
- **Web-Client control** Configure session time, task type, and color
- **User stories for basic functionality** 
	- As a user i want the cube to send start,pause, and stop signals to the webapp so that the app accurately tracks how long a cube has actively run a session. 
	- As a user i want to the web app to send session time to the cube. So that session time can be easily changed.
- **End-to-End features**
	- Web app knows how long cube has run for. 
	- Web app can send how long cube should run. 


**Completed in Sprint 2 (Feature)**

- [ ] **Web UI framework placeholders**
- [ ] **Cube-Client control** can trigger start stops and resets. 
- [ ] **Web-Client control** exposes the endpoint with basic validation
- [ ] **Database framework** integration: data is written to the database
- [ ] **Server** can retrieve the stored data (GET from Firestore)


## 3. Technical Summary: What Was Implemented

This is a **short technical summary** of the **end-to-end feature** you built.

- **Feature:** [**Cube Timer Control**]  
- **Collection:** [**Firestore collection**] (e.g., `features`, `orders`, etc.)  
- **What it does:** [1–2 sentence description]

### Data Model (Firestore)

- **Document shape:**  
  Example JSON that represents **one document** in the collection (or the schema you structured):

![alt text](image-3.png)

  **Why this structure?** We used Firebase Authentication to validate users via email. Then with unique generated uuids we store the information we need. For basica usage we store preset tasks, connected cubes, current session, and session history. 

- **Input (Client → Server):**  
  Example JSON the client sends:

  ```json
  {
    "name": "New Feature",
    "status": "pending"
  }
  ```

- **Output (Server → Client):**  
  Example response the client receives after a successful create or read:

  ```json
  {
    "id": "generated-id",
    "userId": "firebase-uid",
    "name": "New Feature",
    "status": "pending",
    "createdAt": "2026-01-01T12:00:00.000Z"
  }
  ```

---

## 4. End-to-End Flow (What Was Demoed)

**Every JSON request from the cube client is accompanied by the cube 
UUID to link the session activity to a particular user profile.**

**This is a brief description of the Cube client interacting with the server to start a task session**
1. **Client** cube sends a reset request (e.g., POST `/feature`) with a valid **payload** (JSON).
2. **Server** responds with a json with the current time and current task information
3. **Client** Displays current task via GUI
4. **Client** Start button is pressed on client GUI which sends a start task request to the server and Client starts a timer to measure time elapsed along with displaying the task has begun via a faux LED in the GUI.
5. **Server** Once server receives a start task, the server starts a timer to measure elapsed time for web-app display and returns a json to the client that the task has started.
6. **Client** Once client elapsed timer = the task_preset time an 'alert!' is displayed via the GUI.
7. **Client** Once the stop button is pressed the client checks if a task is running (client does nothing if task has not been started) and sends a json stop request to the server which has the elapsed time within the json payload.
8. **Server** Server sends a json POST request to the database with the task_name and elapsed time which is saved in latest session database.

**This is a brief description of the Web-app client interacting with the server to change the current task**
1. **Client** On the web-app client the user selects a different task from the drop down menu this sends a POST with a valid **payload** (JSON) of the new task to update the current active task.
2. **Server** The server validates the uid for authentication
3. **Server** The server updates the database current_task section.
4. **Server** The server updates the databases task_time section to correlate with the task selected.


- **Bounded Read:** In Sprint 2, you were required to demonstrate a **bounded read** (e.g., `.limit()`, `.where()`, or pagination). Describe what you implemented:


- **What you did:** 
- Bound email data to 50 characters, task names to 30 characters : these were done to disable users from adding names of 'infinite' length to prevent attempting to store very large files.
- Bound task time to 99 minutes to prevent users from adding task times of 'infinte' time
- Bound task colour to values within the RGB hex values so users were not adding invalid colours to the cube itself.


---

## 5. Sprint Retrospective: What We Learned

### 5.1 What Went Well

- [Item 1: e.g., “We got end-to-end persistence working faster than expected.”]
- [Item 2: e.g., “We agreed on a consistent validation strategy for the request.”]
- [Item 3: e.g., “Our team communication and coordination improved this sprint.”]

### 5.2 What Didn’t Go Well

- [Item 1: e.g., “We underestimated the time needed to set up Firebase credentials and permissions.”]
- [Item 2: e.g., “Our tests were delayed and didn’t cover all edge cases by demo time.”]
- [Item 3: e.g., “We had integration friction between the client and server around payload format.”]

### 5.3 Key Takeaways & Sprint 3 Actions

| Issue / Challenge | What We Learned | Action for Sprint 3 |
|---|---|---|
| [Issue 1] | [Learning] | [Action] |
| [Issue 2] | [Learning] | [Action] |
| [Issue 3] | [Learning] | [Action] |

---

## 6. Sprint 3 Preview

Based on what we accomplished (and what we didn’t), here are the **next Sprint 3 priorities**:

- [**Priority 1**: e.g., “Add user authentication and authorization so users can only access/modify their own feature data.”]
- [**Priority 2**: e.g., “Expand testing coverage (unit + integration) and implement clearer error handling.”]
- [**Priority 3**: e.g., “Improve read performance with pagination and/or where clauses.”]
