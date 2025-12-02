"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-12-01 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create participants table
    op.create_table(
        'participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create meetings table
    op.create_table(
        'meetings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create meeting_participants junction table
    op.create_table(
        'meeting_participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('pending', 'accepted', 'declined', name='participantstatus'), nullable=False),
        sa.Column('notified_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_id'], ['participants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('meeting_id', 'participant_id', name='uq_meeting_participant')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_meetings_start_time', 'meetings', ['start_time'])
    op.create_index('ix_meetings_end_time', 'meetings', ['end_time'])
    op.create_index('ix_participants_email', 'participants', ['email'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_participants_email', table_name='participants')
    op.drop_index('ix_meetings_end_time', table_name='meetings')
    op.drop_index('ix_meetings_start_time', table_name='meetings')
    
    # Drop tables
    op.drop_table('meeting_participants')
    op.drop_table('meetings')
    op.drop_table('participants')
    
    # Drop enum type
    op.execute('DROP TYPE participantstatus')
