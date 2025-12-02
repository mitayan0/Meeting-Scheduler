# Meeting Scheduler API

A comprehensive FastAPI-based meeting scheduler with PostgreSQL database, featuring meeting management, participant coordination, conflict detection, and ICS calendar export functionality.

## Features

✅ **Meeting Management** - Create, read, update, and delete meetings with full CRUD operations  
✅ **Participant Management** - Manage participants and assign them to meetings  
✅ **Conflict Detection** - Intelligent scheduling conflict detection for overlapping meetings  
✅ **ICS Export** - Export meetings in standard iCalendar format for calendar imports  
✅ **Simulated Notifications** - Logging-based notification system for meeting events  
✅ **RESTful API** - Clean, well-documented API with interactive OpenAPI docs  
✅ **Docker Support** - Full Docker and Docker Compose configuration for easy deployment  
✅ **Database Migrations** - Alembic-based migrations for schema management  
✅ **Automated Tests** - Pytest-based test suite for core functionality

## Technology Stack

- **Backend Framework**: FastAPI 0.109+
- **Database**: PostgreSQL 15 (SQLite for testing)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Testing**: pytest
- **Containerization**: Docker & Docker Compose

## Project Structure

```
meeting-scheduler/
├── app/
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # Database configuration
│   ├── config.py        # Application settings
│   └── main.py          # FastAPI application
├── alembic/             # Database migrations
├── tests/               # Automated tests
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Multi-container setup
└── requirements.txt     # Python dependencies
```

## Installation & Setup

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd meeting-scheduler
```

2. **Start the application with Docker Compose**
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`  
PostgreSQL will be running on port `5432`

3. **Access the interactive API documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Option 2: Local Development

1. **Prerequisites**
- Python 3.11+
- PostgreSQL 15+

2. **Create and activate virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/meeting_scheduler
DEBUG=True
```

5. **Create database**
```bash
createdb meeting_scheduler
```

6. **Run migrations**
```bash
alembic upgrade head
```

7. **Start the application**
```bash
uvicorn app.main:app --reload
```

## API Usage Examples

### 1. Create a Participant

```bash
curl -X POST "http://localhost:8000/api/participants/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com"
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "created_at": "2025-12-01T19:30:00Z"
}
```

### 2. Create a Meeting

```bash
curl -X POST "http://localhost:8000/api/meetings/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Standup",
    "description": "Daily team standup meeting",
    "start_time": "2025-12-05T09:00:00Z",
    "end_time": "2025-12-05T09:30:00Z",
    "location": "Conference Room A",
    "participant_ids": ["550e8400-e29b-41d4-a716-446655440000"]
  }'
```

### 3. Check for Scheduling Conflicts

```bash
curl -X POST "http://localhost:8000/api/conflicts/check" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_ids": ["550e8400-e29b-41d4-a716-446655440000"],
    "start_time": "2025-12-05T09:15:00Z",
    "end_time": "2025-12-05T09:45:00Z"
  }'
```

**Response (with conflict):**
```json
{
  "has_conflicts": true,
  "conflicts": [
    {
      "participant_id": "550e8400-e29b-41d4-a716-446655440000",
      "participant_name": "John Doe",
      "participant_email": "john.doe@example.com",
      "conflicting_meeting_id": "...",
      "conflicting_meeting_title": "Team Standup",
      "conflicting_start_time": "2025-12-05T09:00:00Z",
      "conflicting_end_time": "2025-12-05T09:30:00Z"
    }
  ]
}
```

### 4. Export Meeting as ICS

```bash
curl -X GET "http://localhost:8000/api/meetings/{meeting_id}/export" \
  --output meeting.ics
```

### 5. Get All Meetings for a Participant

```bash
curl -X GET "http://localhost:8000/api/participants/{participant_id}/meetings"
```

### 6. Get Meetings with Filters

```bash
# Filter by date range
curl -X GET "http://localhost:8000/api/meetings/?start_date=2025-12-01T00:00:00Z&end_date=2025-12-31T23:59:59Z"

# Filter by participant
curl -X GET "http://localhost:8000/api/meetings/?participant_id=550e8400-e29b-41d4-a716-446655440000"
```

## Database Schema

### Tables

**meetings**
- `id` (UUID) - Primary key
- `title` (VARCHAR) - Meeting title
- `description` (TEXT) - Optional description
- `start_time` (TIMESTAMP WITH TIMEZONE) - Start time
- `end_time` (TIMESTAMP WITH TIMEZONE) - End time
- `location` (VARCHAR) - Optional location
- `created_at` (TIMESTAMP WITH TIMEZONE)
- `updated_at` (TIMESTAMP WITH TIMEZONE)

**participants**
- `id` (UUID) - Primary key
- `name` (VARCHAR) - Participant name
- `email` (VARCHAR, UNIQUE) - Email address
- `created_at` (TIMESTAMP WITH TIMEZONE)

**meeting_participants** (Junction table)
- `id` (UUID) - Primary key
- `meeting_id` (UUID) - Foreign key to meetings
- `participant_id` (UUID) - Foreign key to participants
- `status` (ENUM) - pending, accepted, declined
- `notified_at` (TIMESTAMP WITH TIMEZONE)
- Unique constraint on (meeting_id, participant_id)

### Relationships

- One meeting can have many participants (many-to-many)
- Cascade delete: Deleting a meeting removes all participant associations
- Email uniqueness enforced at database level

## Architecture & Design Decisions

### 1. **Conflict Detection Algorithm**

The system checks for three types of time overlaps:
- New meeting starts during an existing meeting
- New meeting ends during an existing meeting
- New meeting completely encompasses an existing meeting

### 2. **Timezone Handling**

All timestamps are stored in UTC with timezone awareness (`TIMESTAMP WITH TIMEZONE`), ensuring consistency across different timezones.

### 3. **Notification System**

Implemented as a simulated logging-based system to avoid external dependencies. In production, this can be replaced with actual email sending using services like SendGrid or AWS SES.

### 4. **ICS Export**

Uses the iCalendar standard (RFC 5545) with proper VEVENT components, making exported files compatible with all major calendar applications (Google Calendar, Outlook, Apple Calendar).

### 5. **API Design**

RESTful API following standard conventions:
- POST for creation
- GET for retrieval
- PUT for full updates
- DELETE for removal
- Proper HTTP status codes (201 for creation, 204 for deletion, etc.)

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_meetings.py

# Run with verbose output
pytest -v
```

**Test Coverage:**
- Meeting creation and retrieval
- ICS export functionality
- Conflict detection with various overlap scenarios
- Multiple participant conflict checks

## Future Improvements & Limitations

### Current Limitations

1. **Notification System**: Currently simulated with logging; needs real email integration
2. **Authentication**: No user authentication or authorization implemented
3. **Recurring Meetings**: Does not support recurring meeting patterns
4. **Time Zone Display**: All times returned in UTC; client-side conversion needed
5. **Pagination**: Large meeting lists are not paginated

### Suggested Improvements

1. **Email Integration**: Implement actual email notifications using SMTP or email service APIs
2. **Authentication & Authorization**: Add JWT-based authentication with role-based access control
3. **Recurring Meetings**: Implement RRULE support for recurring meeting patterns
4. **Meeting Reminders**: Add scheduled reminders before meetings
5. **Meeting Status**: Add meeting status (scheduled, in-progress, completed, cancelled)
6. **Participant Response Tracking**: Allow participants to accept/decline meetings
7. **Meeting Attachments**: Support file attachments for meetings
8. **Search Functionality**: Full-text search for meetings and participants
9. **Pagination**: Implement cursor or offset-based pagination for large datasets
10. **Rate Limiting**: Add API rate limiting for production use
11. **Caching**: Implement Redis caching for frequently accessed data
12. **Webhooks**: Support webhooks for meeting event notifications

## API Endpoints Reference

### Meetings

- `POST /api/meetings/` - Create meeting
- `GET /api/meetings/` - List all meetings (with filters)
- `GET /api/meetings/{id}` - Get meeting details
- `PUT /api/meetings/{id}` - Update meeting
- `DELETE /api/meetings/{id}` - Delete meeting
- `GET /api/meetings/{id}/export` - Export as ICS
- `POST /api/meetings/{id}/participants` - Add participant
- `DELETE /api/meetings/{id}/participants/{participant_id}` - Remove participant

### Participants

- `POST /api/participants/` - Create participant
- `GET /api/participants/` - List all participants
- `GET /api/participants/{id}` - Get participant details
- `GET /api/participants/{id}/meetings` - Get participant's meetings

### Conflicts

- `POST /api/conflicts/check` - Check for scheduling conflicts

## License

This project is created for the Alpha Net Python Developer assignment.

## Contact

For questions or issues, please contact the development team.
