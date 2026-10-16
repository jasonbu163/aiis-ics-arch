"""显式新增完整温控样本与投递回执；不修改或导入旧温控记录。

Revision ID: e4f6a8b0c2d4
Revises: d2f4a6b8c0e2
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "e4f6a8b0c2d4"
down_revision = "d2f4a6b8c0e2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("equipment_temperature_samples",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("equipment_id", sa.String(128).with_variant(sa.String(128, collation="utf8mb4_bin"), "mysql"), nullable=False),
        sa.Column("sampled_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column("quality", sa.String(16), nullable=False),
        sa.Column("zone1_set", sa.Numeric(30, 10), nullable=False),
        sa.Column("zone1_act", sa.Numeric(30, 10), nullable=False),
        sa.Column("zone2_set", sa.Numeric(30, 10), nullable=False),
        sa.Column("zone2_act", sa.Numeric(30, 10), nullable=False),
        sa.Column("zone3_set", sa.Numeric(30, 10), nullable=False),
        sa.Column("zone3_act", sa.Numeric(30, 10), nullable=False),
        sa.Column("zone4_set", sa.Numeric(30, 10), nullable=False),
        sa.Column("zone4_act", sa.Numeric(30, 10), nullable=False),
        sa.Column("zone5_set", sa.Numeric(30, 10), nullable=False),
        sa.Column("zone5_act", sa.Numeric(30, 10), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False, server_default=sa.text("(UTC_TIMESTAMP(3))")),
        sa.Column("updated_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False, server_default=sa.text("(UTC_TIMESTAMP(3))")),
        sa.UniqueConstraint("equipment_id", "sampled_at", name="uq_temperature_sample_business"),
        sa.UniqueConstraint("id", "equipment_id", name="uq_temperature_sample_id_equipment"),
        sa.CheckConstraint("quality = 'good'", name="ck_temperature_sample_quality"),
    )
    op.create_index("ix_temperature_sample_equipment_time_id", "equipment_temperature_samples", ["equipment_id", "sampled_at", "id"])
    op.create_table("equipment_temperature_sample_receipts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.String(128).with_variant(sa.String(128, collation="utf8mb4_bin"), "mysql"), nullable=False),
        sa.Column("sample_id", sa.String(128).with_variant(sa.String(128, collation="utf8mb4_bin"), "mysql"), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("sample_record_id", sa.Integer(), nullable=False),
        sa.Column("sampled_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column("outcome", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False, server_default=sa.text("(UTC_TIMESTAMP(3))")),
        sa.Column("updated_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False, server_default=sa.text("(UTC_TIMESTAMP(3))")),
        sa.UniqueConstraint("actor_user_id", "equipment_id", "sample_id", name="uq_temperature_sample_delivery"),
        sa.ForeignKeyConstraint(["sample_record_id", "equipment_id"], ["equipment_temperature_samples.id", "equipment_temperature_samples.equipment_id"], name="fk_temperature_receipt_sample_equipment"),
        sa.CheckConstraint("outcome IN ('created', 'duplicate')", name="ck_temperature_receipt_outcome"),
    )


def downgrade():
    op.drop_table("equipment_temperature_sample_receipts")
    op.drop_table("equipment_temperature_samples")
