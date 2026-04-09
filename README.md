
# Breathing Cube
In today’s digital world, attention is constantly fragmented. Smartphones, notifications, social media feeds, and endless scrolling compete for our focus every minute of the day. The result is chronic distraction, diminished deep focus, and elevated stress levels.

Now imagine being able to step away from that noise, even for a few minutes, and reconnect with your breath.

The BreathingCube is an IoT-enabled device designed to help individuals integrate meditation into busy daily life. Through guided ambient lighting patterns and subtle sound cues, it encourages intentional breathing and mindfulness practice, helping calm the nervous system and restore a sense of presence.

**Course:** Software Systems
**Status:** In Development

## Features 
### Musts
- Press to Meditate
- Web App Control of Cube
- Customizable Colors
- Customizable Breathing Patterns
- Customizable Times

### Shoulds
- Meditation Time/Date Tracking
- Store Previous Session information

### Coulds
- Server Hosted Web App Accesible Online
- Colors Change Based on Time of Day
- Store Data Based on User

### Won'ts
- Synchronized LED animation to music

## About
This is application/product project for a meditation cube.
- Modular Design
- Network Communication
- Security Fundamentals

**Team Members:**
1. Parry Zhuo (Primary Owner)
2. Sasha Roosen-Saba
3. Bryce Reid
4. Kale Wyse

## Testing

### Unit Tests
Run application unit tests (Flask routes, utilities, validation):
```bash
pytest tests/
```

Run a specific test file:
```bash
pytest tests/test_api_cube.py -v
```

### Container & Deployment Tests
Comprehensive containerization testing with pytest + docker-py. Tests verify Docker image builds, runtime health, security compliance, and production readiness.

**Prerequisites:**
- Docker Desktop installed and running
- `docker-compose` available
- Python environment with dependencies installed (`pip install -r requirements.txt`)

**Run all container tests:**
```bash
pytest tests/test_container_*.py -v
```

**Run specific container test category:**
```bash
# Build & image validation
pytest tests/test_container_build.py -v

# Runtime & service health
pytest tests/test_container_runtime.py -v

# Security & compliance
pytest tests/test_container_security.py -v

# Production readiness (gunicorn, logging, performance)
pytest tests/test_container_production.py -v
```

**Run all tests (unit + container):**
```bash
pytest tests/ -v
```

### Local Development with Docker

Start services locally:
```bash
docker compose up --build
```

Stop services:
```bash
docker compose down
```

View logs:
```bash
docker compose logs -f cube-web      # Web service logs
docker compose logs -f cube-api      # API service logs
docker compose logs -f               # All service logs
```

Test service endpoints:
```bash
curl http://localhost:5000/health    # Web service health check
curl http://localhost:5001/health    # API service health check
```

### API Specifications

| Method                    | Route                           | Description                                                             | Auth Required |
|---------------------------|---------------------------------|-------------------------------------------------------------------------|---------------|
| api_task_control          | /api/task/control               | Interface between hardware cube, Firestore database, and timer service. | CUBE_API_KEY  |
| api_get_profile           | /api/profile                    | Get all the current user's profile data.                                | JWT Token     |
| api_get_user_info         | /api/profile/user_info/<field>  | Get the user's user information. (ie. first_name, last_name, etc.)      | JWT Token     |
| api_update_user_info      | /api/profile/user_info          | Update user information. (ie. first_name, last_name, etc.)              | JWT Token     |
| api_save_cube             | /api/profile/cube               | Register a CUBE UUID with a user account.                               | JWT Token     |
| api_get_preset            | /api/profile/preset/<task_name> | Get preset task configurations.                                         | JWT Token     |
| api_create_preset         | /api/profile/preset             | Create new preset task configuration.                                   | JWT Token     |
| api_update_preset         | /api/profile/preset             | Update preset task configuration.                                       | JWT Token     |
| api_delete_preset         | /api/profile/preset             | Delete preset task configuration.                                       | JWT Token     |
| api_get_task              | /api/task/current               | Get the current active task name.                                       | JWT Token     |
| api_set_task              | /api/task/current               | Set the current active task.                                            | JWT Token     |
| api_get_latest_session    | /api/sessions/latest            | Get the latest session data form the session history database.          | JWT Token     |
| api_get_sessions          | /api/sessions                   | Get paginated session list for a user.                                  | JWT Token     |
| api_get_sessions_range    | /api/sessions/range             | Get sessions within a date range.                                       | JWT Token     |
| api_get_sessions_calendar | /api/sessions/calendar          | Get session data aggregated by day for calendar heatmap.                | JWT Token     |
| api_reset_timer           | /api/timer/reset                | Reset web timer to selected preset task time.                           | JWT Token     |
| api_login                 | /login                          | JSON API endpoint for login. Returns a JWT token.                       | None          |
| api_signup                | /signup                         | JSON API endpoint for new user registration.                            | None          |