# Feature Descriptions

## Feature 1: CUBE Simulation Client GUI

**PROBLEM**

Developers need a simple software-based tool 
for testing hardware REST API 

**INPUTS**

- Start Button 
    - &rarr; start task request
    - &rarr; cube UUID
- Stop Button 
    - &rarr; stop task request
    - &rarr; cube UUID
    - &rarr; elapsed time of task execution
- Reset Button
    - &rarr; reset task request
    - &rarr; cube UUID

Note: for testing and development purposes the cube UUID is 
currently hardcoded to match the username "bryce_r"

**OUTPUTS**

- Start Button 
    - &larr; message indicating task started
- Stop Button 
    - &larr; message indicating task stopped
    - &larr; message indicating total preset task time 
      and additional task time saved to the database
- Reset Button
    - &larr; message indicating task reset
    - &larr; current task name
    - &larr; current task time 

**DATA STORED IN FIRESTORE**

- username
- current task name
- current task time
- latest session task name
- latest session task time

**END-TO-END FLOW DESCRIPTION**

Every JSON request from the cube client is accompanied by the cube 
UUID to link the session activity to a particular user profile.

At start up the CUBE client automatically sends a reset task request 
to the server to retrieve the current task information. The server 
returns the current task name and time from the database. The client 
displays the current task information in the GUI.

When the start button is pressed in the client GUI, the client sends 
a start task request to the server, this triggers a timer on the 
server side to begin measuring elapsed time. Simultaneously, a local 
timer starts measuring elapsed time. Additionally, a faux-led indicator
on the GUI display is switched to the on state. When the local client 
timer equals the current preset task time, an "ALERT!" message is 
displayed on th GUI. The server returns a message indicating the task 
started. The cube client must be reset before the start button is 
pressed otherwise nothing will happen.

The cube client must be in the running state before the stop button 
is pressed otherwise nothing will happen. When the stop button is 
pressed in the client GUI, the client sends a stop task request to 
the server, this triggers a timer on the server side to stop measuring
elapsed time. Simultaneously, the local timer stops measuring elapsed 
time. The faux-led indicator on the GUI display is switched to the off
state. The client sends the elapsed time measured by the local timer
to the server. The server saves the current task name and elapsed time
as the latest session information in the database. The server 
calculates the total preset task time and additional time 
completed in the session and returns this information in a message 
in addition to an acknowledgment the task stopped.

The cube client must not be in the running state before the reset 
button is pressed otherwise nothing will happen. When the stop button
is pressed in the client GUI, the client sends a reset task request to
the server, this triggers both the local timer and the timer on the 
server side to reset. If an "ALERT!" message is displayed, it is 
cleared. The server returns the current task name, the current task 
preset time, and a message indicating that the task has been 
reset. The current task information is updated on the client GUI.


## Feature #: "feature title"

**PROBLEM**

**INPUTS**

**OUTPUTS**

**DATA STORED IN FIRESTORE**

**END-TO-END FLOW DESCRIPTION**