"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, index=True),
        sa.Column('password_hash', sa.String(255)),
        sa.Column('full_name', sa.String(255)),
        sa.Column('role', sa.Enum('patient', 'hospital_staff', 'admin', name='roleenum')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Patient profiles
    op.create_table(
        'patient_profiles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), unique=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('emergency_contact', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Departments
    op.create_table(
        'departments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), unique=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Doctors
    op.create_table(
        'doctors',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), unique=True),
        sa.Column('department_id', sa.String(36), sa.ForeignKey('departments.id')),
        sa.Column('specialization', sa.String(200), nullable=True),
        sa.Column('license_number', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Appointment slots
    op.create_table(
        'appointment_slots',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('doctor_id', sa.String(36), sa.ForeignKey('doctors.id')),
        sa.Column('department_id', sa.String(36), sa.ForeignKey('departments.id')),
        sa.Column('start_time', sa.DateTime(timezone=True)),
        sa.Column('end_time', sa.DateTime(timezone=True)),
        sa.Column('is_booked', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Appointments
    op.create_table(
        'appointments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('patient_id', sa.String(36), sa.ForeignKey('patient_profiles.id')),
        sa.Column('doctor_id', sa.String(36), sa.ForeignKey('doctors.id')),
        sa.Column('slot_id', sa.String(36), sa.ForeignKey('appointment_slots.id'), unique=True),
        sa.Column('status', sa.Enum('scheduled', 'confirmed', 'cancelled', 'completed', 'rescheduled', name='appointmentstatus')),
        sa.Column('reason', sa.String(500), nullable=True),
        sa.Column('notes', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Patient documents
    op.create_table(
        'patient_documents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('patient_id', sa.String(36), sa.ForeignKey('patient_profiles.id')),
        sa.Column('filename', sa.String(255)),
        sa.Column('original_filename', sa.String(255)),
        sa.Column('file_path', sa.String(500)),
        sa.Column('file_type', sa.String(50)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('sha256_checksum', sa.String(64), index=True),
        sa.Column('classification', sa.String(50), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('upload_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Workflow runs
    op.create_table(
        'workflow_runs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('patient_id', sa.String(36), sa.ForeignKey('patient_profiles.id')),
        sa.Column('intent', sa.String(200), nullable=True),
        sa.Column('current_step', sa.String(100), nullable=True),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('state_snapshot', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Reminders
    op.create_table(
        'reminders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('appointment_id', sa.String(36), sa.ForeignKey('appointments.id'), unique=True),
        sa.Column('reminder_time', sa.DateTime(timezone=True)),
        sa.Column('message', sa.String(500)),
        sa.Column('is_sent', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Escalations
    op.create_table(
        'escalations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_run_id', sa.String(36), sa.ForeignKey('workflow_runs.id'), nullable=True),
        sa.Column('reason', sa.Text()),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='escalationstatus')),
        sa.Column('reviewer_id', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('decision_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Audit events
    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('event_type', sa.String(100)),
        sa.Column('description', sa.Text()),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

def downgrade() -> None:
    op.drop_table('audit_events')
    op.drop_table('escalations')
    op.drop_table('reminders')
    op.drop_table('workflow_runs')
    op.drop_table('patient_documents')
    op.drop_table('appointments')
    op.drop_table('appointment_slots')
    op.drop_table('doctors')
    op.drop_table('departments')
    op.drop_table('patient_profiles')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS roleenum")
    op.execute("DROP TYPE IF EXISTS appointmentstatus")
    op.execute("DROP TYPE IF EXISTS escalationstatus")