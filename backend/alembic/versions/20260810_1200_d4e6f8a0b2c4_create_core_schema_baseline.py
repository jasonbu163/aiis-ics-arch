"""Create the AIIS ICS Architecture Core schema for a new empty database."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e6f8a0b2c4"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the fourteen Core tables without seed data or project tables."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "token_blacklist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=500), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )

    op.create_table(
        "sys_dicts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dict_type", sa.String(length=50), nullable=False),
        sa.Column("dict_name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "sys_dict_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dict_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=100), nullable=False),
        sa.Column("sort", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("remark", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["dict_id"], ["sys_dicts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # The active-revision FK closes a cycle with projection_mapping_revisions.
    # Add it after both tables exist so a new database can create the schema in
    # dependency order without relying on dialect-specific cycle handling.
    op.create_table(
        "projection_mapping_sets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plc_key", sa.String(length=80), nullable=False),
        sa.Column("db_number", sa.Integer(), nullable=False),
        sa.Column("group_name", sa.String(length=120), nullable=False),
        sa.Column("handler_key", sa.String(length=160), nullable=False),
        sa.Column("active_published_revision_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "plc_key",
            "db_number",
            "group_name",
            "handler_key",
            name="uq_projection_mapping_set_identity",
        ),
    )

    op.create_table(
        "projection_mapping_revisions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("mapping_set_id", sa.Integer(), nullable=False),
        sa.Column("revision_no", sa.Integer(), nullable=False),
        sa.Column("handler_version", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("change_note", sa.Text(), nullable=True),
        sa.Column("validation_report", sa.JSON(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("validated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("published_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="fk_projection_mapping_revision_created_by",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["mapping_set_id"],
            ["projection_mapping_sets.id"],
            name="fk_projection_mapping_revision_set",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["published_by_user_id"],
            ["users.id"],
            name="fk_projection_mapping_revision_published_by",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["validated_by_user_id"],
            ["users.id"],
            name="fk_projection_mapping_revision_validated_by",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "status IN ('draft', 'validated', 'published', 'retired')",
            name="ck_projection_mapping_revision_status",
        ),
        sa.UniqueConstraint(
            "mapping_set_id",
            "revision_no",
            name="uq_projection_mapping_revision_number",
        ),
    )

    op.create_table(
        "projection_mapping_bindings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("revision_id", sa.Integer(), nullable=False),
        sa.Column("plc_key", sa.String(length=80), nullable=False),
        sa.Column("db_number", sa.Integer(), nullable=False),
        sa.Column("group_name", sa.String(length=120), nullable=False),
        sa.Column("point_name", sa.String(length=180), nullable=False),
        sa.Column("input_key", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["revision_id"],
            ["projection_mapping_revisions.id"],
            name="fk_projection_mapping_binding_revision",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "revision_id",
            "input_key",
            name="uq_projection_mapping_binding_input",
        ),
        sa.UniqueConstraint(
            "revision_id",
            "plc_key",
            "db_number",
            "group_name",
            "point_name",
            name="uq_projection_mapping_binding_point",
        ),
    )

    op.create_table(
        "projection_mapping_audit_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("mapping_set_id", sa.Integer(), nullable=False),
        sa.Column("revision_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name="fk_projection_mapping_audit_actor",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["mapping_set_id"],
            ["projection_mapping_sets.id"],
            name="fk_projection_mapping_audit_set",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["revision_id"],
            ["projection_mapping_revisions.id"],
            name="fk_projection_mapping_audit_revision",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "projection_runtime_cursors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("mapping_set_id", sa.Integer(), nullable=False),
        sa.Column("last_raw_snapshot_id", sa.Integer(), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_signature", sa.String(length=255), nullable=True),
        sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["mapping_set_id"],
            ["projection_mapping_sets.id"],
            name="fk_projection_runtime_cursor_set",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mapping_set_id", name="uq_projection_runtime_cursor_set"),
    )

    op.create_table(
        "projection_runtime_audit_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("mapping_set_id", sa.Integer(), nullable=False),
        sa.Column("revision_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("first_raw_snapshot_id", sa.Integer(), nullable=True),
        sa.Column("last_raw_snapshot_id", sa.Integer(), nullable=True),
        sa.Column("processed_snapshot_count", sa.Integer(), nullable=False),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("source_quality", sa.String(length=30), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["mapping_set_id"],
            ["projection_mapping_sets.id"],
            name="fk_projection_runtime_audit_set",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["revision_id"],
            ["projection_mapping_revisions.id"],
            name="fk_projection_runtime_audit_revision",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "event_type IN ('processed', 'skipped', 'contract_rejected', 'failed')",
            name="ck_projection_runtime_audit_event_type",
        ),
    )

    op.create_table(
        "control_agent_gate_tokens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("subject_user_id", sa.Integer(), nullable=False),
        sa.Column("subject_username", sa.String(length=80), nullable=False),
        sa.Column("subject_role", sa.String(length=30), nullable=False),
        sa.Column("issued_by_user_id", sa.Integer(), nullable=False),
        sa.Column("issued_by_username", sa.String(length=80), nullable=False),
        sa.Column("issued_by_role", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("allowed_scopes", sa.JSON(), nullable=False),
        sa.Column("resource_scope", sa.String(length=120), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_by", sa.String(length=80), nullable=True),
        sa.Column("revoke_reason", sa.Text(), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("use_count", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["issued_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["subject_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_control_agent_gate_tokens_hash"),
    )

    op.create_table(
        "monitor_collector_states",
        sa.Column("collector_key", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("worker_id", sa.String(length=120), nullable=True),
        sa.Column("mode", sa.String(length=30), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("target_interval_ms", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sample_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sample_count", sa.Integer(), nullable=False),
        sa.Column("failure_count", sa.Integer(), nullable=False),
        sa.Column("buffered_failure_count", sa.Integer(), nullable=False),
        sa.Column("dropped_sample_count", sa.Integer(), nullable=False),
        sa.Column("last_buffered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_replay_count", sa.Integer(), nullable=False),
        sa.Column("last_collect_duration_ms", sa.Integer(), nullable=True),
        sa.Column("last_write_duration_ms", sa.Integer(), nullable=True),
        sa.Column("last_loop_delay_ms", sa.Integer(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("collector_key"),
    )

    op.create_table(
        "plc_db_block_raw_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plc_key", sa.String(length=80), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("db_number", sa.Integer(), nullable=False),
        sa.Column("group_name", sa.String(length=120), nullable=False),
        sa.Column("contract_version", sa.String(length=120), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("driver", sa.String(length=40), nullable=False),
        sa.Column("quality", sa.String(length=30), nullable=False),
        sa.Column("read_duration_ms", sa.Integer(), nullable=False),
        sa.Column("raw_bytes", sa.LargeBinary(), nullable=True),
        sa.Column("decoded_payload", sa.JSON(), nullable=False),
        sa.Column("unsupported_payload", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "plc_db_block_latest_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plc_key", sa.String(length=80), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("db_number", sa.Integer(), nullable=False),
        sa.Column("group_name", sa.String(length=120), nullable=False),
        sa.Column("contract_version", sa.String(length=120), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("driver", sa.String(length=40), nullable=False),
        sa.Column("quality", sa.String(length=30), nullable=False),
        sa.Column("read_duration_ms", sa.Integer(), nullable=False),
        sa.Column("raw_snapshot_id", sa.Integer(), nullable=True),
        sa.Column("decoded_payload", sa.JSON(), nullable=False),
        sa.Column("unsupported_payload", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "plc_key",
            "db_number",
            "group_name",
            name="uq_plc_db_block_latest_group",
        ),
    )

    op.create_foreign_key(
        "fk_projection_mapping_set_active_revision",
        "projection_mapping_sets",
        "projection_mapping_revisions",
        ["active_published_revision_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_token_blacklist_id", "token_blacklist", ["id"], unique=False)
    op.create_index("ix_sys_dicts_id", "sys_dicts", ["id"], unique=False)
    op.create_index("ix_sys_dicts_dict_type", "sys_dicts", ["dict_type"], unique=True)
    op.create_index("ix_sys_dict_items_id", "sys_dict_items", ["id"], unique=False)
    op.create_index("ix_sys_dict_items_dict_id", "sys_dict_items", ["dict_id"], unique=False)
    op.create_index("ix_projection_mapping_revisions_mapping_set_id", "projection_mapping_revisions", ["mapping_set_id"], unique=False)
    op.create_index("ix_projection_mapping_revisions_status", "projection_mapping_revisions", ["status"], unique=False)
    op.create_index("ix_projection_mapping_bindings_revision_id", "projection_mapping_bindings", ["revision_id"], unique=False)
    op.create_index("ix_projection_mapping_audit_events_mapping_set_id", "projection_mapping_audit_events", ["mapping_set_id"], unique=False)
    op.create_index("ix_projection_mapping_audit_events_revision_id", "projection_mapping_audit_events", ["revision_id"], unique=False)
    op.create_index("ix_projection_mapping_audit_events_action", "projection_mapping_audit_events", ["action"], unique=False)
    op.create_index("ix_projection_runtime_audit_events_mapping_set_id", "projection_runtime_audit_events", ["mapping_set_id"], unique=False)
    op.create_index("ix_projection_runtime_audit_events_revision_id", "projection_runtime_audit_events", ["revision_id"], unique=False)
    op.create_index("ix_projection_runtime_audit_events_event_type", "projection_runtime_audit_events", ["event_type"], unique=False)
    op.create_index("ix_projection_runtime_audit_set_raw", "projection_runtime_audit_events", ["mapping_set_id", "last_raw_snapshot_id"], unique=False)
    op.create_index("ix_control_agent_gate_tokens_id", "control_agent_gate_tokens", ["id"], unique=False)
    op.create_index("ix_control_agent_gate_tokens_subject_user_id", "control_agent_gate_tokens", ["subject_user_id"], unique=False)
    op.create_index("ix_control_agent_gate_tokens_subject_username", "control_agent_gate_tokens", ["subject_username"], unique=False)
    op.create_index("ix_control_agent_gate_tokens_issued_by_user_id", "control_agent_gate_tokens", ["issued_by_user_id"], unique=False)
    op.create_index("ix_control_agent_gate_tokens_status", "control_agent_gate_tokens", ["status"], unique=False)
    op.create_index("ix_control_agent_gate_tokens_expires_at", "control_agent_gate_tokens", ["expires_at"], unique=False)
    op.create_index("ix_control_agent_gate_tokens_subject_status", "control_agent_gate_tokens", ["subject_user_id", "status"], unique=False)
    op.create_index("ix_control_agent_gate_tokens_expiry", "control_agent_gate_tokens", ["status", "expires_at"], unique=False)
    op.create_index("ix_monitor_collector_states_status", "monitor_collector_states", ["status"], unique=False)
    op.create_index("ix_monitor_collector_states_last_heartbeat_at", "monitor_collector_states", ["last_heartbeat_at"], unique=False)
    op.create_index("ix_plc_db_block_raw_snapshots_plc_key", "plc_db_block_raw_snapshots", ["plc_key"], unique=False)
    op.create_index("ix_plc_db_block_raw_snapshots_device_id", "plc_db_block_raw_snapshots", ["device_id"], unique=False)
    op.create_index("ix_plc_db_block_raw_snapshots_db_number", "plc_db_block_raw_snapshots", ["db_number"], unique=False)
    op.create_index("ix_plc_db_block_raw_snapshots_collected_at", "plc_db_block_raw_snapshots", ["collected_at"], unique=False)
    op.create_index("ix_plc_db_block_raw_snapshots_quality", "plc_db_block_raw_snapshots", ["quality"], unique=False)
    op.create_index("ix_plc_db_block_raw_group_time", "plc_db_block_raw_snapshots", ["plc_key", "db_number", "group_name", "collected_at"], unique=False)
    op.create_index("ix_plc_db_block_raw_projection_cursor", "plc_db_block_raw_snapshots", ["plc_key", "db_number", "group_name", "id"], unique=False)
    op.create_index("ix_plc_db_block_latest_snapshots_device_id", "plc_db_block_latest_snapshots", ["device_id"], unique=False)
    op.create_index("ix_plc_db_block_latest_snapshots_collected_at", "plc_db_block_latest_snapshots", ["collected_at"], unique=False)
    op.create_index("ix_plc_db_block_latest_snapshots_quality", "plc_db_block_latest_snapshots", ["quality"], unique=False)
    op.create_index("ix_plc_db_block_latest_snapshots_raw_snapshot_id", "plc_db_block_latest_snapshots", ["raw_snapshot_id"], unique=False)
    op.create_index("ix_plc_db_block_latest_group", "plc_db_block_latest_snapshots", ["plc_key", "db_number", "group_name"], unique=False)


def downgrade() -> None:
    """Drop the Core schema in reverse dependency order."""
    op.drop_constraint(
        "fk_projection_mapping_set_active_revision",
        "projection_mapping_sets",
        type_="foreignkey",
    )

    op.drop_table("plc_db_block_latest_snapshots")
    op.drop_table("plc_db_block_raw_snapshots")
    op.drop_table("monitor_collector_states")
    op.drop_table("control_agent_gate_tokens")
    op.drop_table("projection_runtime_audit_events")
    op.drop_table("projection_runtime_cursors")
    op.drop_table("projection_mapping_audit_events")
    op.drop_table("projection_mapping_bindings")
    op.drop_table("projection_mapping_revisions")
    op.drop_table("projection_mapping_sets")
    op.drop_table("sys_dict_items")
    op.drop_table("sys_dicts")
    op.drop_table("token_blacklist")
    op.drop_table("users")
