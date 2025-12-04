# Meeting Scheduler

A comprehensive FastAPI-based meeting scheduler with PostgreSQL database, featuring meeting management, participant coordination, conflict detection, and ICS calendar export functionality.

## Features

✅ **Meeting Management** - Create, read, update, and delete meetings with full CRUD operations  
✅ **Participant Management** - Manage participants and assign them to meetings  
✅ **Conflict Detection** - Intelligent scheduling conflict detection for overlapping meetings  
✅ **ICS Export** - Export meetings in standard iCalendar format for calendar imports  
✅ **Simulated Notifications** - Logging-based notification system for meeting events  
✅ **RESTful API** - Clean, well-documented API with interactive OpenAPI docs  
✅ **Database Migrations** - Alembic-based migrations for schema management  
✅ **Automated Tests** - Pytest-based test suite for core functionality

## Quick Start

Get the application running in 5 minutes:

```bash
# 1. Clone and navigate to the project
git clone <repository-url>
cd meeting-scheduler

# 2. Set up virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Configure environment (edit .env with your database credentials)
copy .env.example .env

# 4. Create database
createdb -h localhost -p 5431 -U postgres meeting_scheduler

# 5. Set up schema (choose one method)
psql -h localhost -p 5431 -U postgres -d meeting_scheduler -f schema.sql
# OR
alembic upgrade head

# 6. Run the application
uvicorn app.main:app --reload

# 7. Open your browser to http://localhost:8000/docs
```

That's it! You can now test the API using the interactive Swagger UI or import the Postman collection.

## Technology Stack

- **Backend Framework**: FastAPI 0.109+
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Testing**: pytest

## Project Structure

A clean, well-organized project structure adhering to Python best practices:

```
meeting-scheduler/
├── app/
│   ├── routes/          # API endpoints (meetings, participants, conflicts)
│   ├── services/        # Business logic and complex operations
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic schemas for validation
│   ├── database.py      # Database connection and session management
│   ├── config.py        # Application settings and environment variables
│   └── main.py          # FastAPI application entry point
├── alembic/             # Database migrations
│   └── versions/        # Migration files
├── tests/               # Automated tests
│   ├── conftest.py      # Test configuration and fixtures
│   ├── test_meetings.py # Meeting endpoint tests
│   └── test_conflicts.py # Conflict detection tests
├── schema.sql           # Database schema (alternative to Alembic)
├── Meeting_Scheduler_API.postman_collection.json  # Postman collection
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── README.md            # Project documentation
```

## Installation & Execution

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ running locally

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd meeting-scheduler
   ```

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
   
   Create a `.env` file in the root directory (or rename `.env.example`):
   ```env
   # Database Configuration
   # Ensure the port matches your local PostgreSQL installation (default is 5432, user requested 5431)
   DATABASE_URL=postgresql://postgres:postgres@localhost:5431/meeting_scheduler
   
   # Application Configuration
   APP_NAME="Meeting Scheduler API"
   APP_VERSION=1.0.0
   DEBUG=True
   
   # Server Configuration
   HOST=0.0.0.0
   PORT=8000
   ```

5. **Create the database**
   
   Ensure your PostgreSQL server is running, then create the database:
   ```bash
   # Using command line tool if available
   createdb -h localhost -p 5431 -U postgres meeting_scheduler
   
   # OR using SQL shell (psql)
   # CREATE DATABASE meeting_scheduler;
   ```

6. **Set up the database schema**
   
   You have two options:
   
   **Option A: Using schema.sql (Simpler for quick setup)**
   ```bash
   psql -h localhost -p 5431 -U postgres -d meeting_scheduler -f schema.sql
   ```
   
   **Option B: Using Alembic migrations (Recommended for production)**
   ```bash
   alembic upgrade head
   ```
   
   Both methods create the exact same database structure.

7. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`.

8. **Access Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Usage Examples (Postman)

The following examples demonstrate how to use the API with **Postman**. You can also use the interactive **Swagger UI** at `http://localhost:8000/docs`.

### Setting Up Postman

**Option 1: Import the Collection (Recommended)**
1. Open Postman
2. Click **Import** in the top left
3. Select the file: `Meeting_Scheduler_API.postman_collection.json`
4. The collection will be imported with all endpoints and automatic variable management

**Option 2: Manual Setup**
1. **Base URL**: Create an environment variable in Postman:
   - Variable: `base_url`
   - Value: `http://localhost:8000`

2. **Create requests manually** using the examples below

---

### 1. Create a Participant

**Request:**
- **Method**: `POST`
- **URL**: `{{base_url}}/api/participants/`
- **Headers**: 
  - `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com"
}
```

**Expected Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "created_at": "2025-12-04T12:00:00Z"
}
```

> 💡 **Tip**: Save the `id` from the response - you'll need it for creating meetings!

---

### 2. Get All Participants

**Request:**
- **Method**: `GET`
- **URL**: `{{base_url}}/api/participants/`

**Expected Response** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "created_at": "2025-12-04T12:00:00Z"
  }
]
```

---

### 3. Create a Meeting

**Request:**
- **Method**: `POST`
- **URL**: `{{base_url}}/api/meetings/`
- **Headers**: 
  - `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
  "title": "Team Standup",
  "description": "Daily team standup meeting",
  "start_time": "2025-12-05T09:00:00Z",
  "end_time": "2025-12-05T09:30:00Z",
  "location": "Conference Room A",
  "participant_ids": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

**Expected Response** (201 Created):
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Team Standup",
  "description": "Daily team standup meeting",
  "start_time": "2025-12-05T09:00:00Z",
  "end_time": "2025-12-05T09:30:00Z",
  "location": "Conference Room A",
  "created_at": "2025-12-04T12:05:00Z",
  "updated_at": "2025-12-04T12:05:00Z",
  "participants": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "email": "john.doe@example.com",
      "status": "pending"
    }
  ]
}
```

---

### 4. Get All Meetings

**Request:**
- **Method**: `GET`
- **URL**: `{{base_url}}/api/meetings/`

**Expected Response** (200 OK):
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Team Standup",
    "description": "Daily team standup meeting",
    "start_time": "2025-12-05T09:00:00Z",
    "end_time": "2025-12-05T09:30:00Z",
    "location": "Conference Room A",
    "created_at": "2025-12-04T12:05:00Z",
    "updated_at": "2025-12-04T12:05:00Z",
    "participants": [...]
  }
]
```

---

### 5. Check for Scheduling Conflicts

**Request:**
- **Method**: `POST`
- **URL**: `{{base_url}}/api/conflicts/check`
- **Headers**: 
  - `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
  "participant_ids": ["550e8400-e29b-41d4-a716-446655440000"],
  "start_time": "2025-12-05T09:15:00Z",
  "end_time": "2025-12-05T09:45:00Z"
}
```

**Expected Response - With Conflicts** (200 OK):
```json
{
  "has_conflicts": true,
  "conflicts": [
    {
      "participant_id": "550e8400-e29b-41d4-a716-446655440000",
      "participant_name": "John Doe",
      "conflicting_meetings": [
        {
          "id": "660e8400-e29b-41d4-a716-446655440001",
          "title": "Team Standup",
          "start_time": "2025-12-05T09:00:00Z",
          "end_time": "2025-12-05T09:30:00Z"
        }
      ]
    }
  ]
}
```

**Expected Response - No Conflicts** (200 OK):
```json
{
  "has_conflicts": false,
  "conflicts": []
}
```

---

### 6. Update a Meeting

**Request:**
- **Method**: `PUT`
- **URL**: `{{base_url}}/api/meetings/660e8400-e29b-41d4-a716-446655440001`
- **Headers**: 
  - `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
  "title": "Team Standup - Updated",
  "description": "Daily team standup meeting (updated)",
  "start_time": "2025-12-05T09:00:00Z",
  "end_time": "2025-12-05T09:30:00Z",
  "location": "Conference Room B",
  "participant_ids": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

---

### 7. Export Meeting as ICS Calendar File

**Request:**
- **Method**: `GET`
- **URL**: `{{base_url}}/api/meetings/660e8400-e29b-41d4-a716-446655440001/export`

**Expected Response** (200 OK):
- **Content-Type**: `text/calendar; charset=utf-8`
- **Body**: ICS file content

```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Meeting Scheduler//EN
BEGIN:VEVENT
UID:660e8400-e29b-41d4-a716-446655440001
SUMMARY:Team Standup
DESCRIPTION:Daily team standup meeting
DTSTART:20251205T090000Z
DTEND:20251205T093000Z
LOCATION:Conference Room A
END:VEVENT
END:VCALENDAR
```

> 💡 **Tip**: In Postman, click "Save Response" → "Save to a file" to download the `.ics` file, which can be imported into Google Calendar, Outlook, or Apple Calendar.

---

### 8. Delete a Meeting

**Request:**
- **Method**: `DELETE`
- **URL**: `{{base_url}}/api/meetings/660e8400-e29b-41d4-a716-446655440001`

**Expected Response** (204 No Content):
- No response body

---

### 9. Delete a Participant

**Request:**
- **Method**: `DELETE`
- **URL**: `{{base_url}}/api/participants/550e8400-e29b-41d4-a716-446655440000`

**Expected Response** (204 No Content):
- No response body

---

### Postman Collection

You can create a Postman collection with all these requests for easy testing. Alternatively, use the **Swagger UI** at `http://localhost:8000/docs` for interactive API documentation and testing.

## Database Schema

The application uses a normalized relational database schema with three main tables.

### Setup Options

You have **two options** for setting up the database schema:

#### Option 1: Using schema.sql (Simpler)
```bash
# Connect to PostgreSQL and run the schema file
psql -h localhost -p 5431 -U postgres -d meeting_scheduler -f schema.sql
```

#### Option 2: Using Alembic Migrations (Recommended for production)
```bash
# Run migrations
alembic upgrade head
```

Both methods create the exact same database structure.

---

### Tables

1. **participants**
   - `id` (UUID, PK): Unique identifier (auto-generated)
   - `name` (VARCHAR(255)): Participant name
   - `email` (VARCHAR(255), UNIQUE): Email address with validation
   - `created_at` (TIMESTAMP WITH TIMEZONE): Record creation timestamp
   - **Constraint**: Email must be unique and follow valid email format

2. **meetings**
   - `id` (UUID, PK): Unique identifier (auto-generated)
   - `title` (VARCHAR(255)): Meeting title
   - `description` (TEXT): Optional description
   - `start_time` (TIMESTAMP WITH TIMEZONE): Meeting start time
   - `end_time` (TIMESTAMP WITH TIMEZONE): Meeting end time
   - `location` (VARCHAR(255)): Physical or virtual location (optional)
   - `created_at` (TIMESTAMP WITH TIMEZONE): Record creation timestamp
   - `updated_at` (TIMESTAMP WITH TIMEZONE): Last update timestamp
   - **Constraint**: `end_time` must be after `start_time`

3. **meeting_participants** (Junction Table)
   - `id` (UUID, PK): Unique identifier (auto-generated)
   - `meeting_id` (UUID, FK): Reference to meetings table
   - `participant_id` (UUID, FK): Reference to participants table
   - `status` (ENUM): Participant status - 'pending', 'accepted', or 'declined'
   - `notified_at` (TIMESTAMP WITH TIMEZONE): Timestamp of last notification (optional)
   - **Constraint**: Unique combination of (meeting_id, participant_id)
   - **Foreign Keys**: Both foreign keys have `ON DELETE CASCADE`

### Indexes

For optimal query performance, the following indexes are created:
- `ix_participants_email` - Fast email lookups
- `ix_meetings_start_time` - Critical for conflict detection
- `ix_meetings_end_time` - Critical for conflict detection
- `ix_meeting_participants_meeting_id` - Fast join queries
- `ix_meeting_participants_participant_id` - Fast join queries

### Relationships
- **Many-to-Many**: Meetings and Participants are related via the `meeting_participants` junction table
- **Cascading Deletes**: Deleting a meeting or participant automatically removes associated records in `meeting_participants`

### Entity Relationship Diagram (ERD)

```
┌─────────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│  participants   │         │ meeting_participants │         │    meetings     │
├─────────────────┤         ├──────────────────────┤         ├─────────────────┤
│ id (PK)         │◄───────┤ participant_id (FK)  │         │ id (PK)         │
│ name            │         │ meeting_id (FK)      ├────────►│ title           │
│ email (UNIQUE)  │         │ status (ENUM)        │         │ description     │
│ created_at      │         │ notified_at          │         │ start_time      │
└─────────────────┘         └──────────────────────┘         │ end_time        │
                                                              │ location        │
                                                              │ created_at      │
                                                              │ updated_at      │
                                                              └─────────────────┘
```

## Architecture & Design Decisions

### 1. **Layered Architecture**
The application follows a clean layered architecture:
- **Routes (Controllers)**: Handle HTTP requests and responses.
- **Services**: Contain business logic (e.g., conflict checking, export logic).
- **Repositories (via SQLAlchemy)**: Handle database interactions.
- **Schemas (DTOs)**: Define data transfer objects and validation rules.

### 2. **Conflict Detection Strategy**
The system implements a robust overlap detection algorithm that identifies three scenarios:
- New meeting starts during an existing meeting.
- New meeting ends during an existing meeting.
- New meeting completely encompasses an existing meeting.

### 3. **Timezone Handling**
All timestamps are stored and processed in **UTC** to ensure consistency across different timezones. The `TIMESTAMP WITH TIMEZONE` type in PostgreSQL is used to preserve temporal accuracy.

### 4. **Standardized Exports**
The ICS export functionality adheres to **RFC 5545** (iCalendar), ensuring compatibility with major calendar applications like Google Calendar, Outlook, and Apple Calendar.

## Notable Limitations & Future Improvements

### Current Limitations

1. **Notifications**: Currently simulated via logging; no actual email delivery
   - Notifications are logged to console but not sent to participants
   - `notified_at` timestamp is tracked but no real notification occurs

2. **Authentication & Authorization**: No user login or API key protection
   - Anyone can access and modify all meetings and participants
   - No concept of meeting ownership or access control
   - No API rate limiting

3. **Recurring Meetings**: Only single-instance meetings are supported
   - Cannot create daily, weekly, or monthly recurring meetings
   - No support for RRULE (Recurrence Rule) in ICS exports

4. **Pagination**: Large result sets are returned in full
   - GET endpoints return all records without pagination
   - Could cause performance issues with thousands of meetings

5. **Time Zone Display**: All times are stored and returned in UTC
   - No automatic conversion to user's local timezone
   - Frontend applications must handle timezone conversion

6. **Conflict Resolution**: System only detects conflicts, doesn't suggest alternatives
   - No automatic meeting rescheduling suggestions
   - No "find available time slot" functionality

7. **Participant Response Tracking**: Status updates are manual
   - No automated workflow for participants to accept/decline meetings
   - No reminder system for pending responses

### Suggested Future Improvements

1. **Email Integration** 
   - Integrate with SendGrid, AWS SES, or SMTP for real email delivery
   - Send meeting invitations, updates, and cancellations
   - Include ICS attachments in emails for easy calendar imports

2. **Authentication & Authorization**
   - Implement JWT-based authentication (OAuth2)
   - Add user roles (admin, organizer, participant)
   - Implement meeting ownership and access control

3. **Recurring Meetings**
   - Support RRULE for recurring meetings (daily, weekly, monthly)
   - Implement series management (edit single instance vs. entire series)

4. **Smart Scheduling**
   - "Find available time slot" endpoint
   - Suggest alternative times when conflicts are detected
   - Consider participant preferences and working hours

5. **Pagination & Filtering**
   - Add limit/offset pagination for list endpoints
   - Implement filtering by date range, participant, location

## Running Tests
 
 The project includes automated tests using `pytest`. Tests use **SQLite** for simplicity and speed, so no external database setup is required.
 
 ```bash
 # Run all tests
 pytest
 
 # Run with coverage report
 pytest --cov=app
 
 # Run specific test file
 pytest tests/test_meetings.py
 
 # Run with verbose output
 pytest -v
 ```

**Note**: The test database schema is automatically created and dropped for each test to ensure test isolation.

## Additional Resources

### Postman Collection
The repository includes a ready-to-use Postman collection (`Meeting_Scheduler_API.postman_collection.json`) with:
- All API endpoints pre-configured
- Automatic variable extraction (participant_id, meeting_id)
- Example requests with realistic data
- Test scripts for response validation

**To use:**
1. Open Postman
2. Click **Import**
3. Select `Meeting_Scheduler_API.postman_collection.json`
4. Start testing the API!

### Database Schema File
The `schema.sql` file provides a simple alternative to Alembic migrations:
- Complete database schema in plain SQL
- Includes all tables, indexes, and constraints
- Helpful comments explaining each component
- Sample data (commented out) for quick testing
- Useful query examples

**To use:**
```bash
psql -h localhost -p 5431 -U postgres -d meeting_scheduler -f schema.sql
```

## NOTE
Created for the Alpha Net Python Developer assignment.
