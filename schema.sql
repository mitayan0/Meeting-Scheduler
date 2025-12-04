-- Meeting Scheduler Database Schema
-- PostgreSQL 15+

-- It includes three main tables: participants, meetings, and meeting_participants (junction table).

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS meeting_participants CASCADE;
DROP TABLE IF EXISTS meetings CASCADE;
DROP TABLE IF EXISTS participants CASCADE;
DROP TYPE IF EXISTS participantstatus;

-- Create ENUM type for participant status
CREATE TYPE participantstatus AS ENUM ('pending', 'accepted', 'declined');

-- PARTICIPANTS TABLE

-- Stores information about meeting participants
CREATE TABLE participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT participants_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- Index for faster email lookups
CREATE INDEX ix_participants_email ON participants(email);

-- MEETINGS TABLE
-- Stores meeting information
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    location VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure end_time is after start_time
    CONSTRAINT meetings_time_check CHECK (end_time > start_time)
);

-- Indexes for faster time-based queries (critical for conflict detection)
CREATE INDEX ix_meetings_start_time ON meetings(start_time);
CREATE INDEX ix_meetings_end_time ON meetings(end_time);

-- MEETING_PARTICIPANTS TABLE (Junction Table)
-- Many-to-many relationship between meetings and participants
CREATE TABLE meeting_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    participant_id UUID NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    status participantstatus NOT NULL DEFAULT 'pending',
    notified_at TIMESTAMP WITH TIME ZONE,
    
    -- Ensure a participant can only be added once to a meeting
    CONSTRAINT uq_meeting_participant UNIQUE (meeting_id, participant_id)
);

-- Indexes for faster join queries
CREATE INDEX ix_meeting_participants_meeting_id ON meeting_participants(meeting_id);
CREATE INDEX ix_meeting_participants_participant_id ON meeting_participants(participant_id);

-- SAMPLE DATA (Optional - for testing)
-- Uncomment the following lines to insert sample data

-- INSERT INTO participants (name, email) VALUES
--     ('John Doe', 'john.doe@example.com'),
--     ('Jane Smith', 'jane.smith@example.com'),
--     ('Bob Johnson', 'bob.johnson@example.com');

-- INSERT INTO meetings (title, description, start_time, end_time, location) VALUES
--     ('Team Standup', 'Daily team standup meeting', '2025-12-05 09:00:00+00', '2025-12-05 09:30:00+00', 'Conference Room A'),
--     ('Project Review', 'Monthly project review', '2025-12-10 14:00:00+00', '2025-12-10 16:00:00+00', 'Boardroom');

